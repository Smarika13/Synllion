"""Candidate profile database model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Candidate(Base):
    """Candidate profile model."""

    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    headline: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    years_experience: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    current_salary: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    expected_salary: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    education: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    experience: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False,
    )
    projects: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    certifications: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    github_username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    github_repos: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    linkedin_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    portfolio_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    profile_completeness: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
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

    user: Mapped["User"] = relationship(
        "User",
        back_populates="candidate",
    )


# Deferred import to avoid circular imports while satisfying Pylance.
from app.db.models.user import User  # noqa: E402, F401
