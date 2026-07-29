from datetime import datetime
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    details: Optional[dict] = None


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
