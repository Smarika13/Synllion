import uuid
from datetime import datetime

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        Numeric, String, Text)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    years_experience = Column(Integer, nullable=True)
    current_salary = Column(Numeric(12, 2), nullable=True)
    expected_salary = Column(Numeric(12, 2), nullable=True)

    education = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    skills = Column(ARRAY(String), default=list)
    projects = Column(JSON, default=list)
    certifications = Column(JSON, default=list)

    github_username = Column(String(100), nullable=True)
    github_repos = Column(JSON, default=list)
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    profile_completeness = Column(Integer, default=0)
    state = Column(String(50), default="active")

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="candidate")
