import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(30), default="registration")
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(minutes=5),
    )
    attempts_remaining = Column(Integer, default=3)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="otp_verifications")
