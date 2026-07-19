from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class CandidateProfileBase(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    headline: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    location: str | None = Field(default=None, max_length=255)
    years_experience: int | None = Field(default=None, ge=0, le=80)
    current_salary: float | None = Field(default=None, ge=0)
    expected_salary: float | None = Field(default=None, ge=0)

    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)

    github_username: str | None = Field(default=None, max_length=100)
    linkedin_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileUpdate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: str
    user_id: str
    profile_completeness: int
    state: str

    model_config = {"from_attributes": True}
