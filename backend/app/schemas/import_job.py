from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ImportGithubRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    repo_url: str = Field(min_length=1, max_length=500)
    branch: str = "main"
    file_pattern: str = "*.md"
    category_id: str | None = None
    model_id: str | None = None
    tags: list[str] | None = None
    is_public: bool = False


class ImportFileRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    category_id: str | None = None
    model_id: str | None = None
    tags: list[str] | None = None
    is_public: bool = False


class ImportJobResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
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
    model_config = ConfigDict(protected_namespaces=())
    url: str
    format: str
    expires_at: datetime
