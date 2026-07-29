from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.favorite_service import FavoriteService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[dict])
async def list_favorites(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = FavoriteService(session)
    favorites, total = await service.get_user_favorites(current_user.id, page, size)
    return PaginatedResponse(
        items=favorites, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.post("/{prompt_id}", response_model=MessageResponse, status_code=201)
async def add_favorite(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = FavoriteService(session)
    await service.add_favorite(current_user.id, prompt_id)
    return MessageResponse(message="Added to favorites")


@router.delete("/{prompt_id}", response_model=MessageResponse)
async def remove_favorite(
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = FavoriteService(session)
    await service.remove_favorite(current_user.id, prompt_id)
    return MessageResponse(message="Removed from favorites")
