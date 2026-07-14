from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)  # UUID as string for simplicity
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(
        String(20),
        nullable=False,
        default="candidate",
        # Options: candidate, company_admin, company_recruiter, company_viewer, platform_admin
    )
    is_active = Column(Boolean, default=False)  # False until OTP verified
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    otp_verifications = relationship(
        "OTPVerification", back_populates="user", cascade="all, delete-orphan"
    )
    candidate = relationship("Candidate", back_populates="user", uselist=False)
