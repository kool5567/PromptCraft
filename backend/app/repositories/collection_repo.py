from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.repositories.base import BaseRepository
from app.models.collection import Collection, CollectionPrompt


class CollectionRepository(BaseRepository[Collection]):
    _model = Collection

    def __init__(self, session: AsyncSession):
        super().__init__(Collection, session)

    async def get_user_collections(self, user_id: UUID) -> list[Collection]:
        query = select(Collection).where(Collection.user_id == user_id).order_by(Collection.sort_order)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_prompt(self, collection_id: UUID, prompt_id: UUID, user_id: UUID) -> None:
        existing = select(CollectionPrompt).where(
            CollectionPrompt.collection_id == collection_id,
            CollectionPrompt.prompt_id == prompt_id,
        )
        result = await self.session.execute(existing)
        if result.scalar_one_or_none():
            return
        entry = CollectionPrompt(collection_id=collection_id, prompt_id=prompt_id, added_by=user_id)
        self.session.add(entry)
        await self.session.flush()

    async def remove_prompt(self, collection_id: UUID, prompt_id: UUID) -> bool:
        query = delete(CollectionPrompt).where(
            CollectionPrompt.collection_id == collection_id,
            CollectionPrompt.prompt_id == prompt_id,
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def get_items_count(self, collection_id: UUID) -> int:
        query = select(func.count(CollectionPrompt.id)).where(CollectionPrompt.collection_id == collection_id)
        result = await self.session.execute(query)
        return result.scalar() or 0
