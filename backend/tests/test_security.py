from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token
from app.dependencies import get_current_user


def test_access_token_has_access_type() -> None:
    payload = jwt.decode(
        create_access_token({"sub": "user-id"}),
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert payload["type"] == "access"


@pytest.mark.asyncio
async def test_refresh_token_is_rejected_as_api_credential() -> None:
    refresh_token = jwt.encode(
        {
            "sub": "user-id",
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(days=1),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException, match="Invalid authentication credentials"):
        await get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=refresh_token),
            cast(AsyncSession, None),
        )
