from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user, get_optional_user
from app.dependencies.pagination import get_pagination
from app.schemas.prompt import PromptCreateRequest, PromptUpdateRequest, PromptResponse, CopyPromptRequest
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.prompt_service import PromptService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PromptResponse])
async def list_prompts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    category_id: str | None = Query(None),
    model_id: str | None = Query(None),
    current_user=Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    prompts, total = await service.get_public_prompts(
        page=page, size=size,
        category_id=UUID(category_id) if category_id else None,
        model_id=UUID(model_id) if model_id else None,
        search=search,
    )
    return PaginatedResponse(
        items=prompts, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.post("/", response_model=PromptResponse, status_code=201)
async def create_prompt(
    request: PromptCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    return await service.create_prompt(current_user.id, request)


@router.get("/my", response_model=PaginatedResponse[PromptResponse])
async def my_prompts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    prompts, total = await service.get_user_prompts(current_user.id, page, size, status)
    return PaginatedResponse(
        items=prompts, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    current_user=Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    response = await service.get_prompt(prompt_id)
    await service.increment_usage(prompt_id)
    return response


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID,
    request: PromptUpdateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    is_admin = current_user.role in ["admin", "superadmin"]
    return await service.update_prompt(prompt_id, current_user.id, request, is_admin)


@router.delete("/{prompt_id}", response_model=MessageResponse)
async def delete_prompt(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    is_admin = current_user.role in ["admin", "superadmin"]
    await service.delete_prompt(prompt_id, current_user.id, is_admin)
    return MessageResponse(message="Prompt deleted successfully")


@router.post("/{prompt_id}/copy", response_model=PromptResponse)
async def copy_prompt(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    return await service.copy_prompt(prompt_id, current_user.id)
