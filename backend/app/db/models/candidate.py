from datetime import datetime

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        Numeric, String, Text)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True)
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Profile Builder Fields (NO resume upload)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)  # Optional contact only
    headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    years_experience = Column(Integer, nullable=True)
    current_salary = Column(Numeric(12, 2), nullable=True)
    expected_salary = Column(Numeric(12, 2), nullable=True)

    # Profile Builder Sections (structured data, not files)
    education = Column(
        JSON, default=list
    )  # [{institution, degree, field, start_date, end_date, gpa}]
    experience = Column(
        JSON, default=list
    )  # [{company, title, start_date, end_date, description}]
    skills = Column(ARRAY(String), default=list)  # ["Python", "React", "PostgreSQL"]
    projects = Column(
        JSON, default=list
    )  # [{name, description, url, tech_stack, highlights}]
    certifications = Column(JSON, default=list)  # [{name, issuer, date, url}]

    # Social & External
    github_username = Column(String(100), nullable=True)
    github_repos = Column(JSON, default=list)  # Fetched from GitHub API
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    # Profile completeness (0-100%)
    profile_completeness = Column(Integer, default=0)

    # State machine
    state = Column(
        String(50),
        default="active",
        # active, applied, assessment_ready, assessing, submitted, under_review,
        # shortlisted, interview_scheduled, interviewing, selected, rejected,
        # offer_extended, offer_accepted, offer_declined
    )

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="candidate")
