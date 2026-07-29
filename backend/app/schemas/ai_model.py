from pydantic import BaseModel, Field


class AiModelCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: str | None = None
    provider: str = Field(min_length=1, max_length=100)
    category: str = "chat"
    logo_url: str | None = None
    sort_order: int = 0
    metadata: dict | None = None


class AiModelUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    provider: str | None = Field(None, min_length=1, max_length=100)
    category: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None
    metadata: dict | None = None


class AiModelResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    provider: str
    category: str
    logo_url: str | None = None
    is_active: bool
    sort_order: int
    metadata: dict | None = None
    created_at: str
    updated_at: str
