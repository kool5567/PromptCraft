from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    name_ar: str | None = None
    slug: str = Field(min_length=1, max_length=100)
    description: str | None = None
    description_ar: str | None = None
    parent_id: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int = 0


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    name_ar: str | None = None
    slug: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    description_ar: str | None = None
    parent_id: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    name_ar: str | None = None
    slug: str
    description: str | None = None
    description_ar: str | None = None
    parent_id: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int
    is_active: bool
    children: list["CategoryResponse"] = []
    created_at: str
    updated_at: str
