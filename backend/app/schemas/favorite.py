from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from .prompt import PromptListResponse


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    prompt_id: int
    prompt: Optional[PromptListResponse] = None
    created_at: datetime


class ToggleFavoriteResponse(BaseModel):
    is_favorited: bool
    message: str
