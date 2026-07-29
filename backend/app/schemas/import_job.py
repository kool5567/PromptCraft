from pydantic import BaseModel, Field
from datetime import datetime


class ImportGithubRequest(BaseModel):
    repo_url: str = Field(min_length=1, max_length=500)
    branch: str = "main"
    file_pattern: str = "*.md"
    category_id: str | None = None
    model_id: str | None = None
    tags: list[str] | None = None
    is_public: bool = False


class ImportFileRequest(BaseModel):
    category_id: str | None = None
    model_id: str | None = None
    tags: list[str] | None = None
    is_public: bool = False


class ImportJobResponse(BaseModel):
    id: str
    user_id: str
    source_type: str
    source_url: str | None = None
    status: str
    items_total: int
    items_imported: int
    items_failed: int
    error_log: dict | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ExportResponse(BaseModel):
    url: str
    format: str
    expires_at: datetime
