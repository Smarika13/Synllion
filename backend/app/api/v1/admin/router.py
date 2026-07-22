"""Admin review endpoints for company registrations."""

import logging
import secrets
import string
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_password_hash
from app.db.database import get_db
from app.db.models.company import Company
from app.db.models.user import User
from app.dependencies import require_role
from app.services.email import send_company_approval, send_company_rejection

router = APIRouter()
logger = logging.getLogger(__name__)


class PendingCompanyResponse(BaseModel):
    """Summary of a company awaiting review."""

    id: Any
    company_name: str
    email: str
    industry: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RejectRequest(BaseModel):
    """Reason payload for rejecting a company."""

    reason: str = Field(..., min_length=1, max_length=1000)


def _generate_temp_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.get("/companies/pending")
async def list_pending_companies(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> list[dict[str, Any]]:
    """List companies awaiting admin review."""
    result = await db.execute(
        select(Company, User)
        .join(User, Company.user_id == User.id)
        .where(Company.approval_status == "pending")
    )
    return [
        {
            "id": company.id,
            "company_name": company.company_name,
            "email": user.email,
            "industry": company.industry,
            "created_at": company.created_at,
        }
        for company, user in result.all()
    ]


@router.post("/companies/{company_id}/approve")
async def approve_company(
    company_id: Any,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> dict[str, str]:
    """Approve a pending company and email them login credentials."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company: Company | None = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.approval_status != "pending":
        raise HTTPException(status_code=400, detail="Company already reviewed")

    user_result = await db.execute(select(User).where(User.id == company.user_id))
    user: User = user_result.scalar_one()

    temp_password = _generate_temp_password()
    user.password_hash = get_password_hash(temp_password)
    if settings.APP_ENV == "development":
        logger.warning("DEV ONLY — temp password for %s: %s", user.email, temp_password)
    user.is_active = True
    user.is_verified = True

    company.approval_status = "approved"
    company.reviewed_by = admin.id
    company.reviewed_at = datetime.now(UTC)
    company.must_change_password = True

    await db.commit()
    background_tasks.add_task(
        send_company_approval, user.email, user.username, temp_password
    )

    return {"message": "Company approved. Credentials sent by email."}


@router.post("/companies/{company_id}/reject")
async def reject_company(
    company_id: Any,
    request: RejectRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> dict[str, str]:
    """Reject a pending company registration."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company: Company | None = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.approval_status != "pending":
        raise HTTPException(status_code=400, detail="Company already reviewed")

    user_result = await db.execute(select(User).where(User.id == company.user_id))
    user: User = user_result.scalar_one()

    company.approval_status = "rejected"
    company.rejection_reason = request.reason
    company.reviewed_by = admin.id
    company.reviewed_at = datetime.now(UTC)

    await db.commit()
    background_tasks.add_task(send_company_rejection, user.email, request.reason)

    return {"message": "Company registration rejected."}
