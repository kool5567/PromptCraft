from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.repositories.base import BaseRepository
from app.models.import_job import ImportJob


class ImportRepository(BaseRepository[ImportJob]):
    _model = ImportJob

    def __init__(self, session: AsyncSession):
        super().__init__(ImportJob, session)

    async def get_recent_imports(self, limit: int = 50) -> list[ImportJob]:
        query = select(ImportJob).order_by(desc(ImportJob.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
