from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.repositories.collection_repo import CollectionRepository
from app.schemas.collection import CollectionCreateRequest, CollectionUpdateRequest, CollectionResponse


class CollectionService:
    def __init__(self, session: AsyncSession):
        self.repo = CollectionRepository(session)

    async def create_collection(self, user_id: UUID, request: CollectionCreateRequest) -> CollectionResponse:
        collection = await self.repo.create(
            user_id=user_id,
            name=request.name,
            name_ar=request.name_ar,
            description=request.description,
            is_public=request.is_public,
            cover_image=request.cover_image,
        )
        return await self._to_response(collection)

    async def get_collection(self, collection_id: UUID, user_id: UUID) -> CollectionResponse:
        collection = await self.repo.get(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        if collection.user_id != user_id and not collection.is_public:
            raise ForbiddenException("You don't have access to this collection")
        return await self._to_response(collection)

    async def get_user_collections(self, user_id: UUID) -> list[CollectionResponse]:
        collections = await self.repo.get_user_collections(user_id)
        return [await self._to_response(c) for c in collections]

    async def update_collection(self, collection_id: UUID, user_id: UUID, request: CollectionUpdateRequest) -> CollectionResponse:
        collection = await self.repo.get(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        if collection.user_id != user_id:
            raise ForbiddenException("You can only edit your own collections")

        await self.repo.update(collection_id, **request.model_dump(exclude_none=True))
        return await self._to_response(await self.repo.get(collection_id))

    async def delete_collection(self, collection_id: UUID, user_id: UUID) -> None:
        collection = await self.repo.get(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        if collection.user_id != user_id:
            raise ForbiddenException("You can only delete your own collections")
        await self.repo.delete(collection_id)

    async def add_prompt(self, collection_id: UUID, prompt_id: UUID, user_id: UUID) -> None:
        collection = await self.repo.get(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        await self.repo.add_prompt(collection_id, prompt_id, user_id)

    async def remove_prompt(self, collection_id: UUID, prompt_id: UUID, user_id: UUID) -> None:
        collection = await self.repo.get(collection_id)
        if not collection:
            raise NotFoundException("Collection", collection_id)
        if collection.user_id != user_id:
            raise ForbiddenException("You can only modify your own collections")
        removed = await self.repo.remove_prompt(collection_id, prompt_id)
        if not removed:
            raise NotFoundException("Prompt in collection")

    async def _to_response(self, collection) -> CollectionResponse:
        items_count = await self.repo.get_items_count(collection.id)
        return CollectionResponse(
            id=str(collection.id),
            user_id=str(collection.user_id),
            name=collection.name,
            name_ar=collection.name_ar,
            description=collection.description,
            is_public=collection.is_public,
            cover_image=collection.cover_image,
            sort_order=collection.sort_order,
            items_count=items_count,
            created_at=collection.created_at.isoformat() if collection.created_at else "",
            updated_at=collection.updated_at.isoformat() if collection.updated_at else "",
        )
