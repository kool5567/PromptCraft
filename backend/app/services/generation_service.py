from __future__ import annotations

import json
import time
from datetime import date, datetime, timezone
from typing import Any, AsyncGenerator, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import AI_PROVIDERS
from app.core.exceptions import (
    BadRequestException,
    RateLimitException,
    SubscriptionRequiredException,
)
from app.repositories import SubscriptionRepository
from app.schemas.generation import (
    GenerateRequest,
    GenerateResponse,
    GenerateStreamResponse,
)


class GenerationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.sub_repo = SubscriptionRepository(db)

    async def generate(self, user_id: str, request: GenerateRequest) -> GenerateResponse:
        can_proceed = await self.check_quota(user_id)
        if not can_proceed:
            raise RateLimitException("Daily generation limit reached. Upgrade your plan for more.")

        provider = request.ai_provider.lower()
        if provider not in AI_PROVIDERS:
            raise BadRequestException(f"Unsupported AI provider: {provider}")

        start_time = time.monotonic()
        content, tokens_used = await self._call_provider(provider, request)
        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        today = date.today()
        await self.quota_repo.increment_generated(user_id, today)

        return GenerateResponse(
            generated_content=content,
            provider=provider,
            model=request.ai_model,
            tokens_used=tokens_used,
            processing_time_ms=elapsed_ms,
        )

    async def generate_stream(
        self, user_id: str, request: GenerateRequest
    ) -> AsyncGenerator[GenerateStreamResponse, None]:
        can_proceed = await self.check_quota(user_id)
        if not can_proceed:
            raise RateLimitException("Daily generation limit reached")

        provider = request.ai_provider.lower()
        if provider not in AI_PROVIDERS:
            raise BadRequestException(f"Unsupported AI provider: {provider}")

        api_key = self._get_api_key(provider)
        if not api_key:
            mock = self._mock_response(provider, request)
            words = mock.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield GenerateStreamResponse(chunk=chunk, is_finished=False)
            yield GenerateStreamResponse(chunk="", is_finished=True)
            return

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = self._get_headers(provider, api_key)
                body = self._build_request_body(provider, request, stream=True)
                url = self._get_api_url(provider)

                async with client.stream("POST", url, json=body, headers=headers) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        chunk = self._parse_stream_chunk(provider, line)
                        if chunk:
                            yield GenerateStreamResponse(chunk=chunk, is_finished=False)
                    yield GenerateStreamResponse(chunk="", is_finished=True)
        except Exception:
            yield GenerateStreamResponse(chunk="", is_finished=True)

    async def check_quota(self, user_id: str) -> bool:
        subscription = await self.sub_repo.get_by_user(user_id)
        if subscription and subscription.is_active:
            return True

        today = date.today()
        quota = await self.quota_repo.get_or_create(user_id, today)
        return quota.prompts_generated < settings.free_daily_generations

    async def get_available_providers(self) -> dict:
        return dict(AI_PROVIDERS)

    async def _call_provider(self, provider: str, request: GenerateRequest) -> tuple[str, Optional[int]]:
        api_key = self._get_api_key(provider)
        if not api_key:
            return self._mock_response(provider, request), None

        headers = self._get_headers(provider, api_key)
        body = self._build_request_body(provider, request)
        url = self._get_api_url(provider)

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return self._parse_response(provider, data)

    def _get_api_key(self, provider: str) -> Optional[str]:
        key_map = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "deepseek": settings.deepseek_api_key,
            "google": settings.gemini_api_key,
        }
        return key_map.get(provider)

    def _get_api_url(self, provider: str) -> str:
        urls = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "deepseek": "https://api.deepseek.com/chat/completions",
            "google": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            "grok": "https://api.x.ai/v1/chat/completions",
            "mistral": "https://api.mistral.ai/v1/chat/completions",
            "perplexity": "https://api.perplexity.ai/chat/completions",
            "qwen": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "llama": "https://api.together.xyz/v1/chat/completions",
        }
        return urls.get(provider, urls["openai"])

    def _get_headers(self, provider: str, api_key: str) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if provider == "anthropic":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        elif provider == "google":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _build_request_body(self, provider: str, request: GenerateRequest, stream: bool = False) -> dict:
        base = {
            "temperature": request.temperature or 0.7,
            "max_tokens": request.max_tokens or 2048,
        }

        openai_like = {"openai", "deepseek", "grok", "mistral", "perplexity", "llama", "qwen"}

        if provider in openai_like:
            return {
                **base,
                "model": request.ai_model,
                "messages": [{"role": "user", "content": request.prompt_content}],
                "stream": stream,
            }
        elif provider == "anthropic":
            return {
                **base,
                "model": request.ai_model,
                "messages": [{"role": "user", "content": request.prompt_content}],
                "stream": stream,
            }
        elif provider == "google":
            return {
                **base,
                "contents": [{"parts": [{"text": request.prompt_content}]}],
            }
        return {
            **base,
            "model": request.ai_model,
            "messages": [{"role": "user", "content": request.prompt_content}],
            "stream": stream,
        }

    def _parse_response(self, provider: str, data: dict) -> tuple[str, Optional[int]]:
        if provider == "openai" or provider in ("deepseek", "grok", "mistral", "perplexity", "llama", "qwen"):
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens")
            return content.strip(), tokens
        elif provider == "anthropic":
            content = data["content"][0]["text"]
            tokens = data.get("usage", {}).get("output_tokens")
            return content.strip(), tokens
        elif provider == "google":
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return content.strip(), None
        return str(data), None

    def _parse_stream_chunk(self, provider: str, line: str) -> Optional[str]:
        if not line or line.startswith(":"):
            return None

        if line.startswith("data: "):
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                return None
            try:
                data = json.loads(data_str)
                if provider == "anthropic":
                    if data.get("type") == "content_block_delta":
                        return data.get("delta", {}).get("text", "")
                else:
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    return delta.get("content", "")
            except (json.JSONDecodeError, KeyError, IndexError):
                return None

        if provider == "anthropic" and '"type":"content_block_delta"' in line:
            try:
                data = json.loads(line)
                return data.get("delta", {}).get("text", "")
            except (json.JSONDecodeError, KeyError):
                pass

        return None

    def _mock_response(self, provider: str, request: GenerateRequest) -> str:
        return (
            f"This is a simulated response from {provider} ({request.ai_model}).\n\n"
            f"Your prompt was:\n{request.prompt_content}\n\n"
            f"[This is a development mock since no API key is configured for {provider}. "
            f"Set the {provider.upper()}_API_KEY environment variable to get real responses.]"
        )
