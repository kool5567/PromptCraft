from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories import FavoriteRepository, PromptRepository, TemplateRepository
from app.schemas.common import MessageResponse
from app.schemas.favorite import FavoriteResponse
from app.schemas.library import ExportRequest, ExportResponse, LibraryResponse
from app.schemas.prompt import PromptResponse, PromptTagResponse
from app.schemas.template import TemplateResponse, TemplateVariableResponse
from app.schemas.category import CategoryResponse


class LibraryService:
    def __init__(self, db: AsyncSession) -> None:
        self.prompt_repo = PromptRepository(db)
        self.template_repo = TemplateRepository(db)
        self.fav_repo = FavoriteRepository(db)

    async def get_user_library(self, user_id: int) -> dict:
        prompts = await self.prompt_repo.get_user_prompts(user_id)
        templates = await self.template_repo.get_user_templates(user_id)
        favorites = await self.fav_repo.get_user_favorites(user_id)

        prompt_responses = [
            PromptResponse(
                id=str(p.id),
                user_id=str(p.user_id),
                title=p.title,
                title_ar=p.title_ar,
                content=p.content,
                content_ar=p.content_ar,
                description=p.description,
                description_ar=p.description_ar,
                model_id=str(p.model_id) if p.model_id else None,
                category_id=str(p.category_id) if p.category_id else None,
                is_public=p.is_public,
                is_premium=p.is_premium,
                is_template=p.is_template,
                variables=p.variables,
                variables_ar=p.variables_ar,
                usage_count=p.usage_count,
                copy_count=p.copy_count,
                rating_avg=p.rating_avg,
                rating_count=p.rating_count,
                status=p.status.value if hasattr(p.status, "value") else p.status,
                version=p.version,
                tags=[
                    PromptTagResponse(id=str(t.id), name=t.name, slug=t.slug)
                    for t in getattr(p, "tags", []) or []
                ],
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in prompts
        ]

        template_responses = []
        for t in templates:
            cat_resp = None
            if getattr(t, "category", None):
                c = t.category
                cat_resp = CategoryResponse(
                    id=str(c.id), name=c.name, name_ar=c.name_ar, slug=c.slug,
                    description=c.description, description_ar=c.description_ar,
                    parent_id=str(c.parent_id) if c.parent_id else None,
                    icon=c.icon, color=c.color, sort_order=c.sort_order,
                    is_active=c.is_active, children=[],
                    created_at=c.created_at.isoformat() if hasattr(c.created_at, "isoformat") else str(c.created_at),
                    updated_at=c.updated_at.isoformat() if hasattr(c.updated_at, "isoformat") else str(c.updated_at),
                )

            template_responses.append(
                TemplateResponse(
                    id=t.id, uuid=t.uuid, title=t.title, description=t.description,
                    content=t.content, ai_provider=t.ai_provider, ai_model=t.ai_model,
                    category_id=t.category_id, category=cat_resp,
                    is_public=t.is_public, usage_count=t.usage_count,
                    variables=[
                        TemplateVariableResponse(
                            id=v.id, template_id=v.template_id, name=v.name,
                            variable_key=v.variable_key, default_value=v.default_value,
                            description=v.description, is_required=v.is_required,
                            sort_order=v.sort_order,
                        )
                        for v in getattr(t, "variables", []) or []
                    ],
                    user_id=t.user_id, created_at=t.created_at, updated_at=t.updated_at,
                )
            )

        favorite_responses = []
        for fav in favorites:
            p = await self.prompt_repo.get(fav.prompt_id)
            prompt_resp = None
            if p:
                prompt_resp = PromptResponse(
                    id=str(p.id), user_id=str(p.user_id), title=p.title,
                    title_ar=p.title_ar, content=p.content, content_ar=p.content_ar,
                    description=p.description, description_ar=p.description_ar,
                    model_id=str(p.model_id) if p.model_id else None,
                    category_id=str(p.category_id) if p.category_id else None,
                    is_public=p.is_public, is_premium=p.is_premium, is_template=p.is_template,
                    variables=p.variables, variables_ar=p.variables_ar,
                    usage_count=p.usage_count, copy_count=p.copy_count,
                    rating_avg=p.rating_avg, rating_count=p.rating_count,
                    status=p.status.value if hasattr(p.status, "value") else p.status,
                    version=p.version,
                    tags=[PromptTagResponse(id=str(t.id), name=t.name, slug=t.slug) for t in getattr(p, "tags", []) or []],
                    created_at=p.created_at, updated_at=p.updated_at,
                )

            favorite_responses.append(
                FavoriteResponse(
                    id=fav.id, user_id=fav.user_id, prompt_id=fav.prompt_id,
                    prompt=prompt_resp, created_at=fav.created_at,
                )
            )

        return {
            "prompts": prompt_responses,
            "templates": template_responses,
            "favorites": favorite_responses,
        }

    async def export_prompts(self, user_id: int, request: ExportRequest) -> ExportResponse:
        prompts = []
        for pid in request.prompt_ids:
            prompt = await self.prompt_repo.get(pid)
            if prompt and str(prompt.user_id) == str(user_id):
                prompts.append(prompt)

        if request.format == "json":
            data = json.dumps(
                [
                    {
                        "title": p.title,
                        "content": p.content,
                        "description": p.description,
                        "variables": p.variables,
                        "tags": [{"name": t.name, "slug": t.slug} for t in getattr(p, "tags", []) or []],
                        "created_at": p.created_at.isoformat() if hasattr(p.created_at, "isoformat") else str(p.created_at),
                    }
                    for p in prompts
                ],
                indent=2,
            )
            filename = "prompts_export.json"
        elif request.format == "markdown":
            lines = []
            for p in prompts:
                lines.append(f"# {p.title}")
                if p.description:
                    lines.append(f"\n{p.description}\n")
                lines.append(f"\n```\n{p.content}\n```\n")
            data = "\n".join(lines)
            filename = "prompts_export.md"
        else:
            lines = []
            for p in prompts:
                lines.append(f"Title: {p.title}")
                lines.append(f"Description: {p.description or ''}")
                lines.append(f"Content: {p.content}")
                lines.append("---")
            data = "\n".join(lines)
            filename = "prompts_export.txt"

        return ExportResponse(
            data=data,
            format=request.format,
            filename=filename,
        )

    async def copy_prompt_to_library(
        self, user_id: int, prompt_id: str
    ) -> MessageResponse:
        original = await self.prompt_repo.get_prompt_with_relations(prompt_id)
        if not original:
            raise NotFoundException("Prompt", prompt_id)

        await self.prompt_repo.create(
            user_id=user_id,
            title=original.title,
            title_ar=original.title_ar,
            content=original.content,
            content_ar=original.content_ar,
            description=original.description,
            description_ar=original.description_ar,
            model_id=original.model_id,
            category_id=original.category_id,
            is_public=False,
            is_premium=False,
            variables=original.variables,
            variables_ar=original.variables_ar,
            imported_from=f"copied_from:{prompt_id}",
        )

        await self.prompt_repo.increment_copy(prompt_id)

        return MessageResponse(message="Prompt copied to your library successfully")
