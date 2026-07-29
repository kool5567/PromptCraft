from __future__ import annotations

from typing import Optional

from sqlalchemy import desc, select

from app.models.import_log import ImportLog
from app.repositories.base import BaseRepository


class ImportLogRepository(BaseRepository[ImportLog]):
    async def get_by_user(self, user_id: int) -> list[ImportLog]:
        stmt = (
            select(ImportLog)
            .where(ImportLog.imported_by == user_id)
            .order_by(desc(ImportLog.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 10) -> list[ImportLog]:
        stmt = (
            select(ImportLog)
            .order_by(desc(ImportLog.created_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[ImportLog]:
        stmt = (
            select(ImportLog)
            .where(ImportLog.status == status)
            .order_by(desc(ImportLog.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        id: int,
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[ImportLog]:
        instance = await self.get(id)
        if not instance:
            return None
        instance.status = status
        if error_message is not None:
            instance.error_message = error_message
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
