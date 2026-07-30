from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.prompt import Prompt
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    _model = Category

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        stmt = select(Category).where(Category.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_tree(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.parent_id.is_(None), Category.is_active == True)
            .options(selectinload(Category.children))
            .order_by(Category.sort_order)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_prompt_count(self) -> list[dict]:
        stmt = (
            select(
                Category.id,
                Category.name,
                Category.slug,
                Category.icon,
                Category.color,
                Category.sort_order,
                func.count(Prompt.id).label("prompt_count"),
            )
            .outerjoin(
                Prompt,
                Prompt.category_id == Category.id,
            )
            .where(Category.is_active == True)
            .group_by(Category.id)
            .order_by(Category.sort_order)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": row.id,
                "name": row.name,
                "slug": row.slug,
                "icon": row.icon,
                "color": row.color,
                "sort_order": row.sort_order,
                "prompt_count": row.prompt_count,
            }
            for row in rows
        ]
