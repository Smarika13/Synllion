"""Authentication API routes."""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_otp,
    get_password_hash,
    verify_password,
)
from app.db.database import get_db
from app.db.models.candidate import Candidate
from app.db.models.otp import OTPVerification
from app.db.models.user import User

router = APIRouter()


class UserRegisterRequest(BaseModel):
    """Registration request schema."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    user_type: str = Field(..., pattern=r"^(candidate|company_admin)$")


class OTPVerifyRequest(BaseModel):
    """OTP verification request schema."""

    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^[0-9]{6}$")


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


@router.get("/test")
async def test_auth() -> dict[str, str]:
    """Test endpoint for auth router."""
    return {"message": "Auth router working"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Register a new user."""
    existing_email_result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing_email_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username_result = await db.execute(
        select(User).where(User.username == request.username)
    )
    if existing_username_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        user_type=request.user_type,
        is_active=False,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    if request.user_type == "candidate":
        candidate = Candidate(user_id=user.id)
        db.add(candidate)

    otp_code = generate_otp()
    otp = OTPVerification(
        user_id=user.id,
        otp_code=otp_code,
        purpose="registration",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        attempts_remaining=3,
    )
    db.add(otp)
    await db.commit()

    return {
        "message": "Registration successful. Please verify your email with the OTP sent.",
        "email": request.email,
        "expires_in": 300,
    }


@router.post("/verify-otp")
async def verify_otp(
    request: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Verify OTP and activate account."""
    user_result = await db.execute(select(User).where(User.email == request.email))
    user: User | None = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_result = await db.execute(
        select(OTPVerification).where(
            and_(
                OTPVerification.user_id == user.id,
                OTPVerification.otp_code == request.otp_code,
                OTPVerification.purpose == "registration",
                OTPVerification.is_used.is_(False),
                OTPVerification.expires_at > datetime.utcnow(),
                OTPVerification.attempts_remaining > 0,
            )
        )
    )
    otp: OTPVerification | None = otp_result.scalar_one_or_none()

    if not otp:
        existing_otp_result = await db.execute(
            select(OTPVerification).where(
                and_(
                    OTPVerification.user_id == user.id,
                    OTPVerification.purpose == "registration",
                    OTPVerification.is_used.is_(False),
                )
            )
        )
        existing_otp: OTPVerification | None = existing_otp_result.scalar_one_or_none()
        if existing_otp and existing_otp.attempts_remaining > 0:
            existing_otp.attempts_remaining -= 1
            await db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid OTP. {existing_otp.attempts_remaining} attempts remaining.",
            )
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    otp.is_used = True
    user.is_active = True
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "type": user.user_type}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return tokens."""
    user_result = await db.execute(select(User).where(User.email == request.email))
    user: User | None = user_result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please verify your email first.",
        )

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=403, detail="Account locked. Try again later.")

    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "type": user.user_type}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
