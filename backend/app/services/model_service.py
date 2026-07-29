from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.repositories.model_repo import AiModelRepository
from app.schemas.ai_model import AiModelCreateRequest, AiModelUpdateRequest, AiModelResponse


class ModelService:
    def __init__(self, session: AsyncSession):
        self.repo = AiModelRepository(session)

    async def get_active_models(self) -> list[AiModelResponse]:
        models = await self.repo.get_active_models()
        return [self._to_response(m) for m in models]

    async def get_model_by_slug(self, slug: str) -> AiModelResponse:
        model = await self.repo.get_by_slug(slug)
        if not model:
            raise NotFoundException("AI Model", slug)
        return self._to_response(model)

    async def get_models_by_provider(self, provider: str) -> list[AiModelResponse]:
        models = await self.repo.get_by_provider(provider)
        return [self._to_response(m) for m in models]

    async def get_models_by_category(self, category: str) -> list[AiModelResponse]:
        models = await self.repo.get_by_category(category)
        return [self._to_response(m) for m in models]

    async def create_model(self, request: AiModelCreateRequest) -> AiModelResponse:
        existing = await self.repo.get_by_slug(request.slug)
        if existing:
            raise ConflictException(f"Model with slug '{request.slug}' already exists")

        model = await self.repo.create(**request.model_dump())
        return self._to_response(model)

    async def update_model(self, model_id: UUID, request: AiModelUpdateRequest) -> AiModelResponse:
        model = await self.repo.get(model_id)
        if not model:
            raise NotFoundException("AI Model", model_id)

        await self.repo.update(model_id, **request.model_dump(exclude_none=True))
        return self._to_response(await self.repo.get(model_id))

    async def delete_model(self, model_id: UUID) -> None:
        model = await self.repo.get(model_id)
        if not model:
            raise NotFoundException("AI Model", model_id)
        await self.repo.delete(model_id)

    def _to_response(self, model) -> AiModelResponse:
        return AiModelResponse(
            id=str(model.id),
            name=model.name,
            slug=model.slug,
            description=model.description,
            provider=model.provider,
            category=model.category.value if hasattr(model.category, "value") else model.category,
            logo_url=model.logo_url,
            is_active=model.is_active,
            sort_order=model.sort_order,
            extra_data=model.extra_data,
            created_at=model.created_at.isoformat() if model.created_at else "",
            updated_at=model.updated_at.isoformat() if model.updated_at else "",
        )
