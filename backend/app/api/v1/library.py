from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.schemas.prompt import PromptResponse
from app.schemas.common import PaginatedResponse
from app.services.prompt_service import PromptService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PromptResponse])
async def browse_library(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: str | None = Query(None),
    model_id: str | None = Query(None),
    search: str | None = Query(None),
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


@router.get("/featured", response_model=list[PromptResponse])
async def featured_prompts(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    return await service.get_featured_prompts(limit)


@router.get("/recent", response_model=PaginatedResponse[PromptResponse])
async def recent_prompts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    prompts, total = await service.get_public_prompts(page=page, size=size)
    return PaginatedResponse(
        items=prompts, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/popular", response_model=list[PromptResponse])
async def popular_prompts(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    service = PromptService(session)
    return await service.get_featured_prompts(limit)
