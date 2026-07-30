from pydantic import BaseModel, Field, ConfigDict


class GenerateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    description: str = Field(min_length=10, max_length=2000)
    model_id: str | None = None
    category_id: str | None = None
    tone: str | None = None
    language: str = "en"
    temperature: float = 0.7


class EnhanceRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    prompt_content: str = Field(min_length=10)
    instructions: str | None = None
    language: str = "en"


class TranslateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    prompt_content: str = Field(min_length=1)
    target_language: str = "ar"


class SuggestRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    query: str = Field(min_length=2)
    limit: int = 5


class GenerateResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    generated_content: str
    title: str | None = None
    model: str
    tokens_used: int | None = None
    language: str


class CompleteRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    partial_prompt: str = Field(min_length=3)
    context: str | None = None
