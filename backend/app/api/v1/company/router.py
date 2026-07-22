"""Company registration and profile API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.database import get_db
from app.db.models.company import Company
from app.db.models.user import User

router = APIRouter()


class CompanyRegisterRequest(BaseModel):
    """Company registration request schema."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    company_name: str = Field(..., min_length=2, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=500)
    description: str | None = None
    contact_person: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=20)


class CompanyRegisterResponse(BaseModel):
    """Response returned after a company submits registration."""

    message: str
    email: EmailStr


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_company(
    request: CompanyRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> CompanyRegisterResponse:
    """Submit a company registration for admin review.

    No password is set by the company and no OTP is issued here — the
    account stays inactive until an admin approves the application and
    emails real login credentials.
    """
    existing_email = await db.execute(select(User).where(User.email == request.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db.execute(
        select(User).where(User.username == request.username)
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Unusable placeholder — nobody can log in with this. A real password
    # is generated and emailed only when an admin approves the company.
    placeholder_password_hash = get_password_hash(uuid.uuid4().hex)

    user = User(
        username=request.username,
        email=request.email,
        password_hash=placeholder_password_hash,
        user_type="company_admin",
        is_active=False,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    company = Company(
        user_id=user.id,
        company_name=request.company_name,
        registration_number=request.registration_number,
        industry=request.industry,
        website=request.website,
        description=request.description,
        contact_person=request.contact_person,
        contact_phone=request.contact_phone,
        approval_status="pending",
    )
    db.add(company)
    await db.commit()

    return CompanyRegisterResponse(
        message=(
            "Registration submitted. An admin will review your application "
            "and email you login credentials once approved."
        ),
        email=request.email,
    )
