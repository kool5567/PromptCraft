from typing import Generic, TypeVar, Type, Optional, Any, get_args, get_origin
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.sql import Select

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    _model: Type[ModelType] | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for base in getattr(cls, "__orig_bases__", []):
            origin = get_origin(base)
            if origin is BaseRepository:
                args = get_args(base)
                if args:
                    cls._model = args[0]
                    return

    def __init__(self, session: AsyncSession, model: Type[ModelType] | None = None):
        self.model = model or self._model
        self.session = session
        self.db = session

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        column = getattr(self.model, field)
        query = select(self.model).where(column == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[dict] = None,
        sort_field: Optional[str] = None,
        sort_order: str = "desc",
    ) -> tuple[list[ModelType], int]:
        query = select(self.model)
        count_query = select(func.count(self.model.id))

        if filters:
            for field, value in filters.items():
                if value is not None:
                    column = getattr(self.model, field, None)
                    if column is not None:
                        query = query.where(column == value)
                        count_query = count_query.where(column == value)

        if sort_field and hasattr(self.model, sort_field):
            sort_col = getattr(self.model, sort_field)
            query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

        query = query.offset(skip).limit(limit)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        instance = await self.get(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, id: UUID) -> bool:
        instance = await self.get(id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def soft_delete(self, id: UUID) -> bool:
        from datetime import datetime, timezone
        instance = await self.get(id)
        if not instance:
            return False
        if hasattr(instance, "deleted_at"):
            instance.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()
            return True
        return False

    async def count(self, filters: Optional[dict] = None) -> int:
        query = select(func.count(self.model.id))
        if filters:
            for field, value in filters.items():
                if value is not None:
                    column = getattr(self.model, field, None)
                    if column is not None:
                        query = query.where(column == value)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(self, **kwargs) -> bool:
        query = select(self.model.id)
        for field, value in kwargs.items():
            column = getattr(self.model, field, None)
            if column is not None:
                query = query.where(column == value)
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
