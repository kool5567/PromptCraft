from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    q: str = Field(min_length=1, max_length=200)
    category_id: str | None = None
    model_id: str | None = None
    tags: list[str] | None = None
    is_template: bool | None = None
    is_premium: bool | None = None
    language: str | None = None
    sort_by: str = "relevance"
    page: int = 1
    size: int = 20


class SearchSuggestionResponse(BaseModel):
    text: str
    type: str
    score: float
