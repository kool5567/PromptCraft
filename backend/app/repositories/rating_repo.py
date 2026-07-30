from __future__ import annotations

from typing import Optional
from uuid import UUID
from sqlalchemy import func, select

from app.models.rating import PromptRating
from app.repositories.base import BaseRepository


class RatingRepository(BaseRepository[PromptRating]):
    _model = PromptRating

    async def get_user_rating(self, user_id: UUID, prompt_id: UUID) -> Optional[PromptRating]:
        stmt = select(PromptRating).where(
            PromptRating.user_id == user_id,
            PromptRating.prompt_id == prompt_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_prompt_ratings(self, prompt_id: UUID, skip: int = 0, limit: int = 100) -> list[PromptRating]:
        stmt = (
            select(PromptRating)
            .where(PromptRating.prompt_id == prompt_id)
            .order_by(PromptRating.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_average_rating(self, prompt_id: UUID) -> float:
        stmt = select(func.coalesce(func.avg(PromptRating.rating), 0.0)).where(
            PromptRating.prompt_id == prompt_id
        )
        result = await self.session.execute(stmt)
        return float(result.scalar_one())

    async def upsert_rating(
        self, user_id: UUID, prompt_id: UUID, rating: int, review: Optional[str] = None,
    ) -> PromptRating:
        stmt = select(PromptRating).where(
            PromptRating.user_id == user_id,
            PromptRating.prompt_id == prompt_id,
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.rating = rating
            existing.review = review
        else:
            existing = PromptRating(
                user_id=user_id,
                prompt_id=prompt_id,
                rating=rating,
                review=review,
            )
            self.session.add(existing)

        await self.session.flush()
        await self.session.refresh(existing)
        return existing
