from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException
from app.models.prompt import Prompt, PromptStatus, PromptTag
from app.models.tag import Tag
from app.repositories import CategoryRepository, PromptRepository, TagRepository
from app.schemas.prompt import PromptResponse, PromptTagResponse
from app.schemas.search import SearchRequest


class SearchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.prompt_repo = PromptRepository(db)
        self.category_repo = CategoryRepository(db)
        self.tag_repo = TagRepository(db)

    async def search(self, request: SearchRequest) -> dict:
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

        if request.sort_by == "relevance":
            pass
        elif request.sort_by == "newest":
            items.sort(key=lambda p: p.created_at, reverse=True)
        elif request.sort_by == "oldest":
            items.sort(key=lambda p: p.created_at)
        elif request.sort_by == "rating":
            items.sort(key=lambda p: p.rating_avg, reverse=True)
        elif request.sort_by == "popular":
            items.sort(key=lambda p: p.usage_count, reverse=True)

        prompt_responses = [self._to_prompt_response(p) for p in items]
        total = len(prompt_responses)

        facets = await self.get_search_facets(request.q)

        return {
            "items": prompt_responses,
            "total": total,
            "page": request.page,
            "size": request.size,
            "pages": max(1, (total + request.size - 1) // request.size) if request.size > 0 else 1,
            "query": request.q,
            "facets": facets,
        }

    async def full_text_search(
        self,
        q: str,
        filters: Optional[dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        items = await self.prompt_repo.search(q, filters=filters, skip=skip, limit=limit)

        prompt_responses = [self._to_prompt_response(p) for p in items]
        return {
            "items": prompt_responses,
            "total": len(prompt_responses),
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": max(1, (len(prompt_responses) + limit - 1) // limit) if limit > 0 else 1,
            "query": q,
        }

    async def get_search_facets(self, q: str) -> dict:
        pattern = f"%{q}%"

        category_counts = []
        stmt = text("""
            SELECT c.id, c.name, c.slug, COUNT(p.id) as cnt
            FROM categories c
            LEFT JOIN prompts p ON p.category_id = c.id AND p.status = 'published' AND p.is_public = TRUE
            WHERE c.is_active = TRUE
            GROUP BY c.id, c.name, c.slug
            ORDER BY cnt DESC
        """)
        try:
            result = await self.db.execute(stmt)
            for row in result:
                category_counts.append({
                    "id": str(row.id),
                    "name": row.name,
                    "slug": row.slug,
                    "count": row.cnt,
                })
        except Exception:
            pass

        provider_counts = []
        stmt2 = text("""
            SELECT p.model_id, COUNT(p.id) as cnt
            FROM prompts p
            WHERE p.status = 'published' AND p.is_public = TRUE AND p.model_id IS NOT NULL
            GROUP BY p.model_id
            ORDER BY cnt DESC
            LIMIT 20
        """)
        try:
            result2 = await self.db.execute(stmt2)
            for row in result2:
                provider_counts.append({
                    "provider": str(row.model_id),
                    "count": row.cnt,
                })
        except Exception:
            pass

        tag_counts = []
        stmt3 = text("""
            SELECT t.id, t.name, t.slug, COUNT(pt.prompt_id) as cnt
            FROM tags t
            JOIN prompt_tags pt ON pt.tag_id = t.id
            JOIN prompts p ON p.id = pt.prompt_id
            WHERE p.status = 'published' AND p.is_public = TRUE
            GROUP BY t.id, t.name, t.slug
            ORDER BY cnt DESC
            LIMIT 20
        """)
        try:
            result3 = await self.db.execute(stmt3)
            for row in result3:
                tag_counts.append({
                    "id": str(row.id),
                    "name": row.name,
                    "slug": row.slug,
                    "count": row.cnt,
                })
        except Exception:
            pass

        return {
            "categories": category_counts,
            "providers": provider_counts,
            "tags": tag_counts,
        }

    def _to_prompt_response(self, prompt: object) -> PromptResponse:
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
