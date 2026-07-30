from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class VariableSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    name: str
    type: str = "text"
    default: str | None = None
    required: bool = False
    description: str | None = None


class PromptCreateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    title: str = Field(min_length=1, max_length=255)
    title_ar: str | None = None
    content: str = Field(min_length=1)
    content_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    model_id: str | None = None
    category_id: str | None = None
    is_public: bool = False
    is_premium: bool = False
    is_template: bool = False
    variables: list[VariableSchema] | None = None
    variables_ar: list[VariableSchema] | None = None
    tags: list[str] | None = None


class PromptUpdateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    title: str | None = Field(None, min_length=1, max_length=255)
    title_ar: str | None = None
    content: str | None = Field(None, min_length=1)
    content_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    model_id: str | None = None
    category_id: str | None = None
    is_public: bool | None = None
    is_premium: bool | None = None
    is_template: bool | None = None
    variables: list[VariableSchema] | None = None
    variables_ar: list[VariableSchema] | None = None
    tags: list[str] | None = None
    status: str | None = None


class PromptVersionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: str
    prompt_id: str
    content: str
    variables: dict | None = None
    version_number: int
    changelog: str | None = None
    created_by: str
    created_at: datetime


class PromptTagResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: str
    name: str
    slug: str


class PromptResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: str
    user_id: str
    title: str
    title_ar: str | None = None
    content: str
    content_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    model_id: str | None = None
    category_id: str | None = None
    is_public: bool
    is_premium: bool
    is_template: bool
    variables: dict | None = None
    variables_ar: dict | None = None
    usage_count: int
    copy_count: int
    rating_avg: float
    rating_count: int
    status: str
    version: int
    tags: list[PromptTagResponse] = []
    created_at: datetime
    updated_at: datetime


class CopyPromptRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    collection_id: str | None = None


PromptListResponse = PromptResponse
