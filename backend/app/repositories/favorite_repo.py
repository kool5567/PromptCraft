from __future__ import annotations

from sqlalchemy import func, select

from app.models.favorite import Favorite
from app.models.prompt import Prompt
from app.repositories.base import BaseRepository


class FavoriteRepository(BaseRepository[Favorite]):
    _model = Favorite

    async def get_user_favorites(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Favorite]:
        stmt = (
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def is_favorited(self, user_id: int, prompt_id: int) -> bool:
        stmt = select(
            select(Favorite)
            .where(
                Favorite.user_id == user_id,
                Favorite.prompt_id == prompt_id,
            )
            .exists()
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def toggle_favorite(self, user_id: int, prompt_id: int) -> bool:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.prompt_id == prompt_id,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            await self.db.delete(existing)
            await self.db.commit()
            return False

        favorite = Favorite(user_id=user_id, prompt_id=prompt_id)
        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)
        return True

    async def get_favorite_count(self, prompt_id: int) -> int:
        stmt = select(func.count(Favorite.id)).where(
            Favorite.prompt_id == prompt_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
