from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import require_admin
from app.schemas.ai_model import AiModelCreateRequest, AiModelUpdateRequest, AiModelResponse
from app.services.model_service import ModelService

router = APIRouter()


@router.get("/", response_model=list[AiModelResponse])
async def list_models(
    provider: str | None = Query(None),
    category: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    service = ModelService(session)
    if provider:
        return await service.get_models_by_provider(provider)
    if category:
        return await service.get_models_by_category(category)
    return await service.get_active_models()


@router.get("/{slug}", response_model=AiModelResponse)
async def get_model(slug: str, session: AsyncSession = Depends(get_session)):
    service = ModelService(session)
    return await service.get_model_by_slug(slug)


@router.post("/", response_model=AiModelResponse, status_code=201)
async def create_model(
    request: AiModelCreateRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = ModelService(session)
    return await service.create_model(request)


@router.put("/{model_id}", response_model=AiModelResponse)
async def update_model(
    model_id: UUID,
    request: AiModelUpdateRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = ModelService(session)
    return await service.update_model(model_id, request)


@router.delete("/{model_id}")
async def delete_model(
    model_id: UUID,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = ModelService(session)
    await service.delete_model(model_id)
    return {"message": "Model deleted"}
