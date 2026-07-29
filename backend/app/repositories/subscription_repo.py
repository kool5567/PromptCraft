from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
import uuid

from sqlalchemy import func, select

from app.models.subscription import Subscription, UsageQuota
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    async def get_by_user(self, user_id: UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_subscriptions(self, tier: Optional[str] = None) -> list[Subscription]:
        stmt = select(Subscription).where(Subscription.status == "active")
        if tier:
            stmt = stmt.where(Subscription.plan_type == tier)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_subscription_count(self, tier: Optional[str] = None) -> int:
        stmt = select(func.count(Subscription.id)).where(Subscription.status == "active")
        if tier:
            stmt = stmt.where(Subscription.plan_type == tier)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def cancel_subscription(self, user_id: UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.db.execute(stmt)
        subscription = result.scalar_one_or_none()
        if not subscription:
            return None
        subscription.status = "canceled"
        await self.db.flush()
        await self.db.refresh(subscription)
        return subscription


class UsageQuotaRepository(BaseRepository[UsageQuota]):
    async def get_or_create(self, user_id: uuid.UUID, usage_date: datetime) -> UsageQuota:
        from sqlalchemy import select
        stmt = select(UsageQuota).where(
            UsageQuota.user_id == user_id,
            UsageQuota.date == usage_date,
        )
        result = await self.db.execute(stmt)
        quota = result.scalar_one_or_none()
        if quota:
            return quota
        quota = UsageQuota(
            user_id=user_id, date=usage_date,
            prompts_generated=0, prompts_saved=0, api_calls=0,
        )
        self.db.add(quota)
        await self.db.flush()
        await self.db.refresh(quota)
        return quota

    async def increment_generated(self, user_id: uuid.UUID, usage_date: datetime) -> UsageQuota:
        quota = await self.get_or_create(user_id, usage_date)
        quota.prompts_generated += 1
        await self.db.flush()
        await self.db.refresh(quota)
        return quota

    async def increment_saved(self, user_id: uuid.UUID, usage_date: datetime) -> UsageQuota:
        quota = await self.get_or_create(user_id, usage_date)
        quota.prompts_saved += 1
        await self.db.flush()
        await self.db.refresh(quota)
        return quota

    async def get_usage_for_period(self, user_id: uuid.UUID, start_date: datetime, end_date: datetime) -> list[UsageQuota]:
        from sqlalchemy import select
        stmt = (
            select(UsageQuota)
            .where(UsageQuota.user_id == user_id, UsageQuota.date >= start_date, UsageQuota.date <= end_date)
            .order_by(UsageQuota.date)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
