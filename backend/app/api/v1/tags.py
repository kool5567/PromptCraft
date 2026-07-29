from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.tag import TagResponse
from app.services.tag_service import TagService

router = APIRouter()


@router.get("/", response_model=list[TagResponse])
async def list_tags(
    popular: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    service = TagService(session)
    if popular:
        return await service.get_popular_tags(limit)
    return await service.get_all_tags()


@router.get("/{slug}", response_model=TagResponse)
async def get_tag(slug: str, session: AsyncSession = Depends(get_session)):
    service = TagService(session)
    return await service.get_tag_by_slug(slug)
