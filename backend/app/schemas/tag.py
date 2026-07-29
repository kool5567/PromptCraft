from pydantic import BaseModel, Field


class TagResponse(BaseModel):
    id: str
    name: str
    name_ar: str | None = None
    slug: str
    usage_count: int
    created_at: str
    updated_at: str


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    name_ar: str | None = None
    slug: str = Field(min_length=1, max_length=50)
