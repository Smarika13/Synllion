"""User database model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    user_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="candidate",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    otp_verifications: Mapped[list["OTPVerification"]] = relationship(
        "OTPVerification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    candidate: Mapped["Candidate | None"] = relationship(
        "Candidate",
        back_populates="user",
        uselist=False,
    )
    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="user",
        uselist=False,
        foreign_keys="Company.user_id",
    )


# Deferred imports to avoid circular imports while satisfying Pylance.
# These run after the User class is defined, so OTPVerification and
# Candidate can safely reference User in their own bottom imports.
from app.db.models.candidate import Candidate  # noqa: E402, F401
from app.db.models.company import Company  # noqa: E402, F401
from app.db.models.otp import OTPVerification  # noqa: E402, F401
