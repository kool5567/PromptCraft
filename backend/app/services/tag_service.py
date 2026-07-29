from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.tag_repo import TagRepository
from app.schemas.tag import TagResponse


class TagService:
    def __init__(self, session: AsyncSession):
        self.repo = TagRepository(session)

    async def get_all_tags(self) -> list[TagResponse]:
        tags, _ = await self.repo.get_multi(sort_field="name", sort_order="asc")
        return [self._to_response(t) for t in tags]

    async def get_tag_by_slug(self, slug: str) -> TagResponse:
        tag = await self.repo.get_by_slug(slug)
        if not tag:
            raise NotFoundException("Tag", slug)
        return self._to_response(tag)

    async def get_popular_tags(self, limit: int = 20) -> list[TagResponse]:
        tags = await self.repo.get_popular_tags(limit)
        return [self._to_response(t) for t in tags]

    def _to_response(self, tag) -> TagResponse:
        return TagResponse(
            id=str(tag.id),
            name=tag.name,
            name_ar=tag.name_ar,
            slug=tag.slug,
            usage_count=tag.usage_count,
            created_at=tag.created_at.isoformat() if tag.created_at else "",
            updated_at=tag.updated_at.isoformat() if tag.updated_at else "",
        )
