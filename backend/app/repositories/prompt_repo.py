from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.orm import selectinload

from app.models.prompt import Prompt, PromptStatus, PromptTag
from app.models.tag import Tag
from app.repositories.base import BaseRepository


class PromptRepository(BaseRepository[Prompt]):
    async def get_public_prompts(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        tag_ids: Optional[list[int]] = None,
        ai_provider: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> list[Prompt]:
        stmt = (
            select(Prompt)
            .where(Prompt.status == PromptStatus.PUBLISHED, Prompt.is_public == True)
            .options(selectinload(Prompt.user), selectinload(Prompt.category), selectinload(Prompt.tags))
        )

        if category_id is not None:
            stmt = stmt.where(Prompt.category_id == category_id)

        if tag_ids:
            stmt = stmt.where(
                Prompt.id.in_(
                    select(PromptTag.prompt_id).where(PromptTag.tag_id.in_(tag_ids))
                )
            )

        if ai_provider:
            stmt = stmt.join(Prompt.model_rel).where(
                Prompt.model_rel.has(provider=ai_provider)
            )

        sort_column = getattr(Prompt, sort_by, Prompt.created_at)
        stmt = stmt.order_by(desc(sort_column)).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def search(
        self,
        q: str,
        filters: Optional[dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Prompt]:
        pattern = f"%{q}%"
        stmt = (
            select(Prompt)
            .where(
                Prompt.status == PromptStatus.PUBLISHED,
                or_(
                    Prompt.title.ilike(pattern),
                    Prompt.description.ilike(pattern),
                    Prompt.content.ilike(pattern),
                ),
            )
            .options(selectinload(Prompt.user), selectinload(Prompt.category), selectinload(Prompt.tags))
        )

        if filters:
            if filters.get("category_id"):
                stmt = stmt.where(Prompt.category_id == filters["category_id"])
            if filters.get("ai_provider"):
                stmt = stmt.join(Prompt.model_rel).where(
                    Prompt.model_rel.has(provider=filters["ai_provider"])
                )
            if filters.get("is_premium") is not None:
                stmt = stmt.where(Prompt.is_premium == filters["is_premium"])
            if filters.get("tag_ids"):
                stmt = stmt.where(
                    Prompt.id.in_(
                        select(PromptTag.prompt_id).where(
                            PromptTag.tag_id.in_(filters["tag_ids"])
                        )
                    )
                )

        stmt = stmt.order_by(desc(Prompt.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_user_prompts(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Prompt]:
        stmt = (
            select(Prompt)
            .where(Prompt.user_id == user_id, Prompt.deleted_at.is_(None))
            .options(selectinload(Prompt.category), selectinload(Prompt.tags))
            .order_by(desc(Prompt.updated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_featured_prompts(
        self, skip: int = 0, limit: int = 100
    ) -> list[Prompt]:
        stmt = (
            select(Prompt)
            .where(
                Prompt.status == PromptStatus.PUBLISHED,
                Prompt.is_public == True,
                Prompt.rating_avg >= 4.0,
                Prompt.rating_count >= 5,
            )
            .options(selectinload(Prompt.user), selectinload(Prompt.category), selectinload(Prompt.tags))
            .order_by(desc(Prompt.rating_avg))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def increment_view(self, prompt_id: UUID) -> None:
        stmt = (
            update(Prompt)
            .where(Prompt.id == prompt_id)
            .values(usage_count=Prompt.usage_count + 1)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def increment_copy(self, prompt_id: UUID) -> None:
        stmt = (
            update(Prompt)
            .where(Prompt.id == prompt_id)
            .values(copy_count=Prompt.copy_count + 1)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_popular(self, limit: int = 10) -> list[Prompt]:
        stmt = (
            select(Prompt)
            .where(Prompt.status == PromptStatus.PUBLISHED, Prompt.is_public == True)
            .options(selectinload(Prompt.user), selectinload(Prompt.category))
            .order_by(desc(Prompt.usage_count))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_recent(self, limit: int = 10) -> list[Prompt]:
        stmt = (
            select(Prompt)
            .where(Prompt.status == PromptStatus.PUBLISHED, Prompt.is_public == True)
            .options(selectinload(Prompt.user), selectinload(Prompt.category))
            .order_by(desc(Prompt.created_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_provider(
        self, provider: str, skip: int = 0, limit: int = 100
    ) -> list[Prompt]:
        stmt = (
            select(Prompt)
            .where(
                Prompt.status == PromptStatus.PUBLISHED,
                Prompt.is_public == True,
            )
            .join(Prompt.model_rel)
            .where(Prompt.model_rel.has(provider=provider))
            .options(selectinload(Prompt.user), selectinload(Prompt.category), selectinload(Prompt.tags))
            .order_by(desc(Prompt.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_prompt_with_relations(
        self, prompt_id: UUID
    ) -> Optional[Prompt]:
        stmt = (
            select(Prompt)
            .where(Prompt.id == prompt_id)
            .options(
                selectinload(Prompt.user),
                selectinload(Prompt.category),
                selectinload(Prompt.tags),
                selectinload(Prompt.versions),
                selectinload(Prompt.model_rel),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
