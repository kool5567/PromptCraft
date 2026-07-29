from pydantic import BaseModel, Field
from typing import Optional

from .prompt import PromptListResponse
from .template import TemplateResponse
from .favorite import FavoriteResponse


class LibraryResponse(BaseModel):
    prompts: list[PromptListResponse] = []
    templates: list[TemplateResponse] = []
    favorites: list[FavoriteResponse] = []


class ExportRequest(BaseModel):
    prompt_ids: list[int]
    format: str = Field(default="json", pattern="^(json|markdown|text)$")


class ExportResponse(BaseModel):
    data: str
    format: str
    filename: str
