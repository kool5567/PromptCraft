from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from .category import CategoryResponse


class TemplateVariableCreate(BaseModel):
    name: str = Field(max_length=255)
    variable_key: str = Field(max_length=255)
    default_value: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=1000)
    is_required: Optional[bool] = True
    sort_order: Optional[int] = None


class TemplateCreate(BaseModel):
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    content: str
    ai_provider: Optional[str] = Field(default=None, max_length=100)
    ai_model: Optional[str] = Field(default=None, max_length=100)
    category_id: Optional[int] = None
    is_public: Optional[bool] = True
    variables: list[TemplateVariableCreate] = []


class TemplateUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    content: Optional[str] = None
    ai_provider: Optional[str] = Field(default=None, max_length=100)
    ai_model: Optional[str] = Field(default=None, max_length=100)
    category_id: Optional[int] = None
    is_public: Optional[bool] = None
    variables: Optional[list[TemplateVariableCreate]] = None


class TemplateVariableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    name: str
    variable_key: str
    default_value: Optional[str] = None
    description: Optional[str] = None
    is_required: bool
    sort_order: Optional[int] = None


class TemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    title: str
    description: Optional[str] = None
    content: str
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    is_public: bool
    usage_count: int
    variables: list[TemplateVariableResponse] = []
    user_id: int
    created_at: datetime
    updated_at: datetime
