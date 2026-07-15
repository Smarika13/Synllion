import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), default="registration")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(minutes=5),
    )
    attempts_remaining: Mapped[int] = mapped_column(Integer, default=3)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="otp_verifications")
