from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.repositories import TemplateRepository
from app.schemas.common import MessageResponse
from app.schemas.template import (
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
    TemplateVariableResponse,
)
from app.schemas.category import CategoryResponse


class TemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self.template_repo = TemplateRepository(db)

    async def create(self, user_id: int, data: TemplateCreate) -> TemplateResponse:
        template = await self.template_repo.create(
            user_id=user_id,
            title=data.title,
            description=data.description,
            content=data.content,
            ai_provider=data.ai_provider,
            ai_model=data.ai_model,
            category_id=data.category_id,
            is_public=data.is_public,
        )

        if data.variables:
            for var in data.variables:
                await self.template_repo.create(
                    template_id=template.id,
                    name=var.name,
                    variable_key=var.variable_key,
                    default_value=var.default_value,
                    description=var.description,
                    is_required=var.is_required,
                    sort_order=var.sort_order,
                )

        return await self._to_response(template)

    async def get(self, template_id: int) -> TemplateResponse:
        template = await self.template_repo.get_with_variables(template_id)
        if not template:
            raise NotFoundException("Template", template_id)

        return await self._to_response(template)

    async def update(self, template_id: int, user_id: int, data: TemplateUpdate) -> TemplateResponse:
        template = await self.template_repo.get(template_id)
        if not template:
            raise NotFoundException("Template", template_id)

        if template.user_id != user_id:
            raise ForbiddenException("You can only edit your own templates")

        update_data = {}
        for field in ["title", "description", "content", "ai_provider",
                       "ai_model", "category_id", "is_public"]:
            val = getattr(data, field, None)
            if val is not None:
                update_data[field] = val

        if update_data:
            template = await self.template_repo.update(template_id, **update_data)
            if not template:
                raise NotFoundException("Template", template_id)

        return await self._to_response(template)

    async def delete(self, template_id: int, user_id: int) -> MessageResponse:
        template = await self.template_repo.get(template_id)
        if not template:
            raise NotFoundException("Template", template_id)

        if template.user_id != user_id:
            raise ForbiddenException("You can only delete your own templates")

        await self.template_repo.delete(template_id)
        return MessageResponse(message="Template deleted successfully")

    async def list_public(
        self,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TemplateResponse]:
        templates = await self.template_repo.get_public_templates(
            category_id=category_id,
            skip=skip,
            limit=limit,
        )
        return [await self._to_response(t) for t in templates]

    async def get_user_templates(self, user_id: int) -> list[TemplateResponse]:
        templates = await self.template_repo.get_user_templates(user_id)
        return [await self._to_response(t) for t in templates]

    async def _to_response(self, template: object) -> TemplateResponse:
        category_response = None
        if getattr(template, "category", None):
            cat = template.category
            category_response = CategoryResponse(
                id=str(cat.id),
                name=cat.name,
                name_ar=cat.name_ar,
                slug=cat.slug,
                description=cat.description,
                description_ar=cat.description_ar,
                parent_id=str(cat.parent_id) if cat.parent_id else None,
                icon=cat.icon,
                color=cat.color,
                sort_order=cat.sort_order,
                is_active=cat.is_active,
                children=[],
                created_at=cat.created_at.isoformat() if hasattr(cat.created_at, "isoformat") else str(cat.created_at),
                updated_at=cat.updated_at.isoformat() if hasattr(cat.updated_at, "isoformat") else str(cat.updated_at),
            )

        variables = []
        for var in getattr(template, "variables", []) or []:
            variables.append(
                TemplateVariableResponse(
                    id=var.id,
                    template_id=var.template_id,
                    name=var.name,
                    variable_key=var.variable_key,
                    default_value=var.default_value,
                    description=var.description,
                    is_required=var.is_required,
                    sort_order=var.sort_order,
                )
            )

        return TemplateResponse(
            id=template.id,
            uuid=template.uuid,
            title=template.title,
            description=template.description,
            content=template.content,
            ai_provider=template.ai_provider,
            ai_model=template.ai_model,
            category_id=template.category_id,
            category=category_response,
            is_public=template.is_public,
            usage_count=template.usage_count,
            variables=variables,
            user_id=template.user_id,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
