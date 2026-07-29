from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class ImportCreate(BaseModel):
    source: str = Field(max_length=255)
    source_url: Optional[str] = None


class ImportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    source: str
    source_url: Optional[str] = None
    total_items: Optional[int] = None
    imported_items: Optional[int] = None
    failed_items: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    imported_by: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime


class ImportListResponse(BaseModel):
    imports: list[ImportResponse]
    pagination: dict
