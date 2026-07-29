from pydantic import BaseModel, Field
from typing import Optional


class GenerateRequest(BaseModel):
    prompt_content: str
    ai_provider: str = Field(max_length=100)
    ai_model: str = Field(max_length=100)
    parameters: Optional[dict] = {}
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=16384)


class GenerateResponse(BaseModel):
    generated_content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None


class GenerateStreamResponse(BaseModel):
    chunk: str
    is_finished: bool
