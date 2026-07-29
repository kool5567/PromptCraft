from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.prompt import PromptResponse
from app.schemas.common import PaginatedResponse
from app.services.prompt_service import PromptService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[PromptResponse])
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: str | None = Query(None),
    model_id: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    from uuid import UUID
    service = PromptService(session)
    prompts, total = await service.get_public_prompts(
        page=page, size=size, search=q,
        category_id=UUID(category_id) if category_id else None,
        model_id=UUID(model_id) if model_id else None,
    )
    return PaginatedResponse(
        items=prompts, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=2, max_length=100),
    session: AsyncSession = Depends(get_session),
):
    from app.repositories.tag_repo import TagRepository
    repo = TagRepository(session)
    tags = await repo.search(q)
    return [
        {"text": t.name, "type": "tag", "score": float(t.usage_count)}
        for t in tags[:5]
    ]
