"""One-off script to create the first admin user."""

import asyncio
import uuid

from app.core.security import get_password_hash
from app.db.database import async_session
from app.db.models.user import User


async def main() -> None:
    async with async_session() as db:
        user = User(
            id=uuid.uuid4(),
            username="synllion_admin",
            email="admin@synllion.dev",
            password_hash=get_password_hash("YourAdminPassword123"),
            user_type="admin",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        print(f"Created admin: {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
