from __future__ import annotations

from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from app.models.template import Template
from app.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    async def get_user_templates(self, user_id: int) -> list[Template]:
        stmt = (
            select(Template)
            .where(Template.user_id == user_id)
            .order_by(desc(Template.updated_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_public_templates(
        self,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Template]:
        stmt = (
            select(Template)
            .where(Template.is_public == True)
            .options(selectinload(Template.user), selectinload(Template.category))
        )
        if category_id is not None:
            stmt = stmt.where(Template.category_id == category_id)
        stmt = stmt.order_by(desc(Template.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_variables(self, template_id: int) -> Optional[Template]:
        stmt = (
            select(Template)
            .where(Template.id == template_id)
            .options(selectinload(Template.variables))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
