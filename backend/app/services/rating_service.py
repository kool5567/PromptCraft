from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.repositories import PromptRepository, RatingRepository
from app.schemas.rating import RatingCreate, RatingResponse, RatingUpdate


class RatingService:
    def __init__(self, db: AsyncSession) -> None:
        self.rating_repo = RatingRepository(db)
        self.prompt_repo = PromptRepository(db)

    async def rate_prompt(
        self, user_id: int, prompt_id: int, data: RatingCreate
    ) -> RatingResponse:
        prompt = await self.prompt_repo.get(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        existing = await self.rating_repo.get_user_rating(user_id, prompt_id)
        if existing:
            raise BadRequestException("You have already rated this prompt")

        rating = await self.rating_repo.upsert_rating(
            user_id=user_id,
            prompt_id=prompt_id,
            score=data.score,
            comment=data.comment,
        )

        avg = await self.rating_repo.get_average_rating(prompt_id)
        ratings_list = await self.rating_repo.get_prompt_ratings(prompt_id, limit=1000)
        prompt.rating_avg = avg
        prompt.rating_count = len(ratings_list)

        return await self._to_response(rating)

    async def update_rating(
        self, user_id: int, prompt_id: int, data: RatingUpdate
    ) -> RatingResponse:
        prompt = await self.prompt_repo.get(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        existing = await self.rating_repo.get_user_rating(user_id, prompt_id)
        if not existing:
            raise NotFoundException("Rating")

        if data.score is not None:
            existing.rating = data.score
        if data.comment is not None:
            existing.review = data.comment

        rating = await self.rating_repo.upsert_rating(
            user_id=user_id,
            prompt_id=prompt_id,
            score=existing.rating,
            comment=existing.review,
        )

        avg = await self.rating_repo.get_average_rating(prompt_id)
        ratings_list = await self.rating_repo.get_prompt_ratings(prompt_id, limit=1000)
        prompt.rating_avg = avg
        prompt.rating_count = len(ratings_list)

        return await self._to_response(rating)

    async def get_prompt_ratings(
        self, prompt_id: int, skip: int = 0, limit: int = 100
    ) -> list[RatingResponse]:
        prompt = await self.prompt_repo.get(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        ratings = await self.rating_repo.get_prompt_ratings(
            prompt_id, skip=skip, limit=limit
        )

        return [await self._to_response(r) for r in ratings]

    async def _to_response(self, rating: object) -> RatingResponse:
        user_obj = getattr(rating, "user", None)
        user_response = None
        if user_obj:
            from app.schemas.auth import UserResponse
            user_response = UserResponse(
                id=str(user_obj.id),
                email=user_obj.email,
                username=user_obj.username,
                role=user_obj.role.value if hasattr(user_obj.role, "value") else user_obj.role,
                subscription_tier=user_obj.subscription_tier.value if hasattr(user_obj.subscription_tier, "value") else user_obj.subscription_tier,
                is_active=user_obj.is_active,
                is_email_verified=user_obj.is_email_verified,
                profile_image=user_obj.profile_image,
                created_at=user_obj.created_at.isoformat() if hasattr(user_obj.created_at, "isoformat") else str(user_obj.created_at),
                updated_at=user_obj.updated_at.isoformat() if hasattr(user_obj.updated_at, "isoformat") else str(user_obj.updated_at),
            )

        return RatingResponse(
            id=rating.id,
            user_id=rating.user_id,
            prompt_id=rating.prompt_id,
            score=rating.rating if hasattr(rating, "rating") else rating.score,
            comment=getattr(rating, "review", None) or getattr(rating, "comment", None),
            user=user_response,
            created_at=rating.created_at,
            updated_at=getattr(rating, "updated_at", rating.created_at),
        )
