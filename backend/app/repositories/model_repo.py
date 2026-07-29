from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.ai_model import AiModel


class AiModelRepository(BaseRepository[AiModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(AiModel, session)

    async def get_by_slug(self, slug: str) -> AiModel | None:
        query = select(AiModel).where(AiModel.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_models(self) -> list[AiModel]:
        query = select(AiModel).where(AiModel.is_active == True).order_by(AiModel.sort_order)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_provider(self, provider: str) -> list[AiModel]:
        query = select(AiModel).where(AiModel.provider == provider, AiModel.is_active == True).order_by(AiModel.sort_order)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[AiModel]:
        query = select(AiModel).where(AiModel.category == category, AiModel.is_active == True).order_by(AiModel.sort_order)
        result = await self.session.execute(query)
        return list(result.scalars().all())
