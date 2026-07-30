from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select, update

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    _model = User

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_users(
        self, q: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        pattern = f"%{q}%"
        stmt = (
            select(User)
            .where(
                or_(
                    User.email.ilike(pattern),
                    User.username.ilike(pattern),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_users_count(self) -> int:
        stmt = select(func.count(User.id)).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_subscriber_count(self, tier: Optional[str] = None) -> int:
        stmt = select(func.count(User.id)).where(
            User.subscription_tier.isnot(None),
            User.is_active == True,
        )
        if tier:
            stmt = stmt.where(User.subscription_tier == tier)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_daily_active_users(self, date: date) -> int:
        stmt = select(func.count(User.id)).where(
            func.date(User.last_login) == date,
            User.is_active == True,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def increment_daily_count(self, user_id: UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def reset_daily_counts(self) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(User)
            .where(func.date(User.last_login) < func.date(now))
            .values(last_login=None)
        )
        await self.db.execute(stmt)
        await self.db.commit()
