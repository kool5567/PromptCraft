from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

from .auth import UserResponse


class RatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("rating")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=2000)


class RatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    prompt_id: UUID
    rating: int
    review: Optional[str] = None
    user: Optional[UserResponse] = None
    created_at: datetime
