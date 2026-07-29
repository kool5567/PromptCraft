from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.repositories.favorite_repo import FavoriteRepository


class FavoriteService:
    def __init__(self, session: AsyncSession):
        self.repo = FavoriteRepository(session)

    async def add_favorite(self, user_id: UUID, prompt_id: UUID) -> dict:
        exists = await self.repo.is_favorited(user_id, prompt_id)
        if exists:
            raise ConflictException("Already in favorites")

        fav = await self.repo.create(user_id=user_id, prompt_id=prompt_id)
        return {"id": str(fav.id), "prompt_id": str(fav.prompt_id)}

    async def remove_favorite(self, user_id: UUID, prompt_id: UUID) -> None:
        removed = await self.repo.remove_favorite(user_id, prompt_id)
        if not removed:
            raise NotFoundException("Favorite")

    async def get_user_favorites(self, user_id: UUID, page: int = 1, size: int = 20) -> tuple[list[dict], int]:
        skip = (page - 1) * size
        favorites, total = await self.repo.get_user_favorites(user_id, skip, size)
        result = [
            {
                "id": str(f.id),
                "prompt_id": str(f.prompt_id),
                "created_at": f.created_at.isoformat(),
            }
            for f in favorites
        ]
        return result, total
