from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.models.setting import SiteSetting
from app.repositories.base import BaseRepository


class SiteSettingsRepository(BaseRepository[SiteSetting]):
    _model = SiteSetting

    async def get_by_key(self, key: str) -> Optional[SiteSetting]:
        stmt = select(SiteSetting).where(SiteSetting.key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_public_settings(self) -> list[SiteSetting]:
        stmt = select(SiteSetting).where(SiteSetting.is_public == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_setting(
        self,
        key: str,
        value: str,
        type: str = "string",
        description: Optional[str] = None,
    ) -> SiteSetting:
        stmt = select(SiteSetting).where(SiteSetting.key == key)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.value = value
            existing.type = type
            if description is not None:
                existing.description = description
        else:
            existing = SiteSetting(
                key=key,
                value=value,
                type=type,
                description=description,
            )
            self.db.add(existing)

        await self.db.commit()
        await self.db.refresh(existing)
        return existing
