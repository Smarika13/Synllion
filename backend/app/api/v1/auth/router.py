from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
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


@router.get("/test")
async def test_auth():
    return {"message": "Auth router working"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: dict, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    # Check if email exists
    result = await db.execute(select(User).where(User.email == request["email"]))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username exists
    result = await db.execute(select(User).where(User.username == request["username"]))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user (inactive until OTP verified)
    user = User(
        username=request["username"],
        email=request["email"],
        password_hash=get_password_hash(request["password"]),
        user_type=request["user_type"],
        is_active=False,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    # Create profile based on user type
    if request["user_type"] == "candidate":
        candidate = Candidate(user_id=user.id)
        db.add(candidate)

    # Generate OTP
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

    # TODO: Send OTP email via background task
    # background_tasks.add_task(send_otp_email, request["email"], otp_code)

    return {
        "message": "Registration successful. Please verify your email with the OTP sent.",
        "email": request["email"],
        "expires_in": 300,
    }


@router.post("/verify-otp")
async def verify_otp(request: dict, db: AsyncSession = Depends(get_db)):
    email = request.get("email")
    otp_code = request.get("otp_code")

    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find valid OTP
    result = await db.execute(
        select(OTPVerification).where(
            and_(
                OTPVerification.user_id == user.id,
                OTPVerification.otp_code == otp_code,
                OTPVerification.purpose == "registration",
                OTPVerification.is_used == False,
                OTPVerification.expires_at > datetime.utcnow(),
                OTPVerification.attempts_remaining > 0,
            )
        )
    )
    otp = result.scalar_one_or_none()

    if not otp:
        # Decrement attempts if wrong OTP
        result = await db.execute(
            select(OTPVerification).where(
                and_(
                    OTPVerification.user_id == user.id,
                    OTPVerification.purpose == "registration",
                    OTPVerification.is_used == False,
                )
            )
        )
        existing_otp = result.scalar_one_or_none()
        if existing_otp and existing_otp.attempts_remaining > 0:
            existing_otp.attempts_remaining -= 1
            await db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid OTP. {existing_otp.attempts_remaining} attempts remaining.",
            )
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Mark OTP as used and activate user
    otp.is_used = True
    user.is_active = True
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()

    # Generate tokens
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "type": user.user_type}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/login")
async def login(request: dict, db: AsyncSession = Depends(get_db)):
    email = request.get("email")
    password = request.get("password")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please verify your email first.",
        )

    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "type": user.user_type}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
