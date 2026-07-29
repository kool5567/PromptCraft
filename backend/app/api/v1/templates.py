from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user, get_optional_user
from app.schemas.prompt import PromptCreateRequest, PromptResponse
from app.schemas.common import PaginatedResponse
from app.services.prompt_service import PromptService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PromptResponse])
async def list_templates(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    prompts, total = await service.get_public_prompts(page=page, size=size)
    templates = [p for p in prompts if p.is_template]
    return PaginatedResponse(
        items=templates, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/{template_id}", response_model=PromptResponse)
async def get_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    return await service.get_prompt(template_id)


@router.post("/", response_model=PromptResponse, status_code=201)
async def create_template(
    request: PromptCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    request.is_template = True
    service = PromptService(session)
    return await service.create_prompt(current_user.id, request)


@router.post("/{template_id}/use", response_model=PromptResponse)
async def use_template(
    template_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    return await service.copy_prompt(template_id, current_user.id)
