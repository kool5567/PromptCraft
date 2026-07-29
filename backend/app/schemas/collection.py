from pydantic import BaseModel, Field


class CollectionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    name_ar: str | None = None
    description: str | None = None
    is_public: bool = False
    cover_image: str | None = None


class CollectionUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    name_ar: str | None = None
    description: str | None = None
    is_public: bool | None = None
    cover_image: str | None = None


class CollectionPromptResponse(BaseModel):
    id: str
    prompt_id: str
    added_by: str
    sort_order: int
    created_at: str


class CollectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    is_public: bool
    cover_image: str | None = None
    sort_order: int
    items_count: int = 0
    created_at: str
    updated_at: str


class AddToCollectionRequest(BaseModel):
    prompt_id: str
