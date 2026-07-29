from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    description: str = Field(min_length=10, max_length=2000)
    model_id: str | None = None
    category_id: str | None = None
    tone: str | None = None
    language: str = "en"
    temperature: float = 0.7


class EnhanceRequest(BaseModel):
    prompt_content: str = Field(min_length=10)
    instructions: str | None = None
    language: str = "en"


class TranslateRequest(BaseModel):
    prompt_content: str = Field(min_length=1)
    target_language: str = "ar"


class SuggestRequest(BaseModel):
    query: str = Field(min_length=2)
    limit: int = 5


class GenerateResponse(BaseModel):
    generated_content: str
    title: str | None = None
    model: str
    tokens_used: int | None = None
    language: str


class CompleteRequest(BaseModel):
    partial_prompt: str = Field(min_length=3)
    context: str | None = None
