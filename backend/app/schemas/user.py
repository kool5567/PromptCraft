from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=500)
    website: str | None = Field(None, max_length=255)
    github_username: str | None = Field(None, max_length=100)
    preferences: dict | None = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    display_name: str | None = None
    bio: str | None = None
    website: str | None = None
    github_username: str | None = None
    preferences: dict | None = None
    created_at: str
    updated_at: str


class UserStatsResponse(BaseModel):
    total_prompts: int
    total_public_prompts: int
    total_collections: int
    total_favorites: int
    total_generations: int
    total_copies: int


class UserUpdateRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    profile_image: str | None = None
