from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.candidate import Candidate
from app.db.models.user import User
from app.dependencies import get_current_user
from app.schemas.candidate import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
)

router = APIRouter()


def calculate_profile_completeness(candidate: Candidate) -> int:
    fields = [
        bool(candidate.full_name),
        bool(candidate.phone),
        bool(candidate.headline),
        bool(candidate.summary),
        bool(candidate.location),
        candidate.years_experience is not None,
        len(candidate.skills) > 0,
        len(candidate.education) > 0,
        len(candidate.experience) > 0,
        len(candidate.projects) > 0,
        bool(candidate.linkedin_url),
        bool(candidate.github_username),
    ]
    score = int((sum(fields) / len(fields)) * 100)
    return score


@router.get("/profile", response_model=CandidateProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Candidate:
    if current_user.user_type != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access profile builder",
        )

    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate: Candidate | None = result.scalar_one_or_none()
    if candidate is None:
        candidate = Candidate(user_id=current_user.id)
        db.add(candidate)
        await db.flush()

    candidate.profile_completeness = calculate_profile_completeness(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.post("/profile", response_model=CandidateProfileResponse)
async def create_or_replace_profile(
    payload: CandidateProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Candidate:
    if current_user.user_type != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access profile builder",
        )

    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate: Candidate | None = result.scalar_one_or_none()
    if candidate is None:
        candidate = Candidate(user_id=current_user.id)
        db.add(candidate)
        await db.flush()

    for key, value in payload.model_dump().items():
        setattr(candidate, key, value)

    candidate.profile_completeness = calculate_profile_completeness(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.patch("/profile", response_model=CandidateProfileResponse)
async def update_profile(
    payload: CandidateProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Candidate:
    if current_user.user_type != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can access profile builder",
        )

    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate: Candidate | None = result.scalar_one_or_none()
    if candidate is None:
        candidate = Candidate(user_id=current_user.id)
        db.add(candidate)
        await db.flush()

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(candidate, key, value)

    candidate.profile_completeness = calculate_profile_completeness(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate
