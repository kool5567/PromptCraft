from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.common import MessageResponse

router = APIRouter()


@router.post("/{prompt_id}/rate", response_model=MessageResponse)
async def rate_prompt(
    prompt_id: UUID,
    rating: int,
    review: str | None = None,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from app.models.rating import PromptRating
    existing = await session.get(PromptRating, (prompt_id, current_user.id))
    if existing:
        existing.rating = rating
        existing.review = review
    else:
        session.add(PromptRating(prompt_id=prompt_id, user_id=current_user.id, rating=rating, review=review))
    await session.flush()
    return MessageResponse(message="Rating submitted")


@router.get("/{prompt_id}/ratings")
async def get_ratings(
    prompt_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import select
    from app.models.rating import PromptRating
    query = select(PromptRating).where(PromptRating.prompt_id == prompt_id)
    result = await session.execute(query)
    ratings = result.scalars().all()
    return [
        {"id": str(r.id), "user_id": str(r.user_id), "rating": r.rating, "review": r.review, "created_at": r.created_at.isoformat()}
        for r in ratings
    ]
