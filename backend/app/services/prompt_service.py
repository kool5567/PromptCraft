from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.prompt import PromptStatus
from app.repositories import PromptRepository, TagRepository
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.prompt import (
    PromptCreateRequest,
    PromptResponse,
    PromptTagResponse,
    PromptUpdateRequest,
)
from app.schemas.search import SearchRequest


class PromptService:
    def __init__(self, db: AsyncSession) -> None:
        self.prompt_repo = PromptRepository(db)
        self.tag_repo = TagRepository(db)

    async def create_prompt(self, user_id: str, data: PromptCreateRequest) -> PromptResponse:
        prompt = await self.prompt_repo.create(
            user_id=user_id,
            title=data.title,
            title_ar=data.title_ar,
            content=data.content,
            content_ar=data.content_ar,
            description=data.description,
            description_ar=data.description_ar,
            model_id=data.model_id,
            category_id=data.category_id,
            is_public=data.is_public,
            is_premium=data.is_premium,
            is_template=data.is_template,
            variables=data.variables,
            variables_ar=data.variables_ar,
            status=PromptStatus.PUBLISHED if data.is_public else PromptStatus.DRAFT,
        )

        if data.tags:
            for tag_slug in data.tags:
                tag = await self.tag_repo.get_by_slug(tag_slug)
                if tag:
                    prompt.tags.append(tag)
                    await self.tag_repo.increment_usage(tag.id)

        return await self._to_prompt_response(prompt)

    async def get_prompt(
        self, prompt_id: str, with_relations: bool = True
    ) -> PromptResponse:
        if with_relations:
            prompt = await self.prompt_repo.get_prompt_with_relations(prompt_id)
        else:
            prompt = await self.prompt_repo.get(prompt_id)

        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        await self.prompt_repo.increment_view(prompt_id)
        return await self._to_prompt_response(prompt)

    async def update_prompt(
        self, prompt_id: str, user_id: str, data: PromptUpdateRequest
    ) -> PromptResponse:
        prompt = await self.prompt_repo.get_prompt_with_relations(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        if str(prompt.user_id) != str(user_id):
            raise ForbiddenException("You can only edit your own prompts")

        update_data = {}
        for field in [
            "title", "title_ar", "content", "content_ar", "description",
            "description_ar", "model_id", "category_id", "is_public",
            "is_premium", "is_template", "variables", "variables_ar", "status",
        ]:
            val = getattr(data, field, None)
            if val is not None:
                update_data[field] = val

        if update_data:
            prompt = await self.prompt_repo.update(prompt_id, **update_data)
            if not prompt:
                raise NotFoundException("Prompt", prompt_id)

        if data.tags is not None:
            for tag in list(prompt.tags):
                await self.tag_repo.decrement_usage(tag.id)
                prompt.tags.remove(tag)

            for tag_slug in data.tags:
                tag = await self.tag_repo.get_by_slug(tag_slug)
                if tag:
                    prompt.tags.append(tag)
                    await self.tag_repo.increment_usage(tag.id)

        return await self._to_prompt_response(prompt)

    async def delete_prompt(self, prompt_id: str, user_id: str) -> MessageResponse:
        prompt = await self.prompt_repo.get(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        if str(prompt.user_id) != str(user_id):
            raise ForbiddenException("You can only delete your own prompts")

        await self.prompt_repo.soft_delete(prompt_id)
        return MessageResponse(message="Prompt deleted successfully")

    async def list_public_prompts(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        tag_ids: Optional[list[int]] = None,
        ai_provider: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> PaginatedResponse:
        items = await self.prompt_repo.get_public_prompts(
            skip=skip,
            limit=limit,
            category_id=category_id,
            tag_ids=tag_ids,
            ai_provider=ai_provider,
            sort_by=sort_by,
        )
        total = await self.prompt_repo.count(filters={"status": PromptStatus.PUBLISHED, "is_public": True})
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1

        prompt_responses = [await self._to_prompt_response(p) for p in items]
        return PaginatedResponse(
            items=prompt_responses,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )

    async def get_public_prompts(
        self,
        page: int = 1,
        size: int = 20,
        category_id: Optional[str] = None,
        model_id: Optional[str] = None,
        search: Optional[str] = None,
        is_template: Optional[bool] = None,
    ) -> tuple[list, int]:
        skip = (page - 1) * size
        filters = {"status": PromptStatus.PUBLISHED, "is_public": True}
        if category_id:
            filters["category_id"] = category_id
        if is_template is not None:
            filters["is_template"] = is_template

        ai_provider = None
        if model_id:
            from app.repositories import AiModelRepository
            model_repo = AiModelRepository(self.prompt_repo.session)
            model = await model_repo.get_by_field("id", model_id)
            if model:
                ai_provider = model.provider

        if search:
            if ai_provider:
                filters["ai_provider"] = ai_provider
            items = await self.prompt_repo.search(q=search, filters=filters if filters else None, skip=skip, limit=size)
        else:
            items = await self.prompt_repo.get_public_prompts(
                skip=skip, limit=size,
                category_id=filters.get("category_id"),
                ai_provider=ai_provider,
            )
        total = await self.prompt_repo.count(filters={"status": PromptStatus.PUBLISHED, "is_public": True})
        return [await self._to_prompt_response(p) for p in items], total

    async def get_featured_prompts(self, limit: int = 10) -> list:
        items = await self.prompt_repo.get_public_prompts(skip=0, limit=limit, sort_by="usage_count")
        return [await self._to_prompt_response(p) for p in items]

    async def get_user_prompts(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        items = await self.prompt_repo.get_user_prompts(user_id, skip=skip, limit=limit)
        total = await self.prompt_repo.count(filters={"user_id": user_id})
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1

        prompt_responses = [await self._to_prompt_response(p) for p in items]
        return PaginatedResponse(
            items=prompt_responses,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )

    async def search_prompts(self, request: SearchRequest) -> dict:
        filters = {}
        if request.category_id:
            filters["category_id"] = request.category_id
        if request.model_id:
            filters["ai_provider"] = request.model_id
        if request.tags:
            filters["tag_ids"] = request.tags
        if request.is_template is not None:
            filters["is_template"] = request.is_template
        if request.is_premium is not None:
            filters["is_premium"] = request.is_premium

        skip = (request.page - 1) * request.size
        items = await self.prompt_repo.search(
            q=request.q,
            filters=filters if filters else None,
            skip=skip,
            limit=request.size,
        )
        total = len(items)

        prompt_responses = [await self._to_prompt_response(p) for p in items]
        return {
            "items": prompt_responses,
            "total": total,
            "page": request.page,
            "size": request.size,
            "pages": max(1, (total + request.size - 1) // request.size) if request.size > 0 else 1,
            "query": request.q,
            "facets": {},
        }

    async def get_prompt_stats(self, prompt_id: str) -> dict:
        prompt = await self.prompt_repo.get(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        from app.repositories import FavoriteRepository, RatingRepository
        fav_repo = FavoriteRepository(self.prompt_repo.session)
        rating_repo = RatingRepository(self.prompt_repo.session)

        favorite_count = await fav_repo.get_favorite_count(prompt_id)
        avg_rating = await rating_repo.get_average_rating(prompt_id)
        ratings = await rating_repo.get_prompt_ratings(prompt_id, limit=1000)

        return {
            "views": prompt.usage_count,
            "copies": prompt.copy_count,
            "favorites": favorite_count,
            "rating_avg": avg_rating,
            "rating_count": len(ratings),
            "version": prompt.version,
        }

    async def _to_prompt_response(self, prompt: Any) -> PromptResponse:
        return PromptResponse(
            id=str(prompt.id),
            user_id=str(prompt.user_id),
            title=prompt.title,
            title_ar=prompt.title_ar,
            content=prompt.content,
            content_ar=prompt.content_ar,
            description=prompt.description,
            description_ar=prompt.description_ar,
            model_id=str(prompt.model_id) if prompt.model_id else None,
            category_id=str(prompt.category_id) if prompt.category_id else None,
            is_public=prompt.is_public,
            is_premium=prompt.is_premium,
            is_template=prompt.is_template,
            variables=prompt.variables,
            variables_ar=prompt.variables_ar,
            usage_count=prompt.usage_count,
            copy_count=prompt.copy_count,
            rating_avg=prompt.rating_avg,
            rating_count=prompt.rating_count,
            status=prompt.status.value if hasattr(prompt.status, "value") else prompt.status,
            version=prompt.version,
            tags=[
                PromptTagResponse(id=str(t.id), name=t.name, slug=t.slug)
                for t in getattr(prompt, "tags", []) or []
            ],
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )
