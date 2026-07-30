from __future__ import annotations

from typing import Optional

from sqlalchemy import desc, select, update

from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    _model = Tag

    async def get_by_slug(self, slug: str) -> Optional[Tag]:
        stmt = select(Tag).where(Tag.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, q: str) -> list[Tag]:
        pattern = f"%{q}%"
        stmt = select(Tag).where(Tag.name.ilike(pattern)).limit(20)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_popular(self, limit: int = 10) -> list[Tag]:
        stmt = (
            select(Tag)
            .order_by(desc(Tag.usage_count))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def increment_usage(self, tag_id: int) -> None:
        stmt = (
            update(Tag)
            .where(Tag.id == tag_id)
            .values(usage_count=Tag.usage_count + 1)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def decrement_usage(self, tag_id: int) -> None:
        stmt = (
            update(Tag)
            .where(Tag.id == tag_id, Tag.usage_count > 0)
            .values(usage_count=Tag.usage_count - 1)
        )
        await self.db.execute(stmt)
        await self.db.commit()
