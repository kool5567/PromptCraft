import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.config import settings
from app.core.exceptions import BadRequestException, SubscriptionRequiredException
from app.repositories.user_repo import UserRepository
from app.schemas.generator import GenerateRequest, GenerateResponse, EnhanceRequest


class GeneratorService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def generate_prompt(self, user_id: str, request: GenerateRequest) -> GenerateResponse:
        user = await self.user_repo.get(user_id)
        if not user:
            raise BadRequestException("User not found")

        if user.subscription_tier.value == "free" and not await self._check_daily_limit(user_id):
            raise SubscriptionRequiredException("Free tier limit reached. Upgrade to continue.")

        system_prompt = self._build_system_prompt(request)
        result = await self._call_ai_api(system_prompt, request)

        await self._log_generation(user_id)

        return GenerateResponse(
            generated_content=result["content"],
            title=result.get("title"),
            model=result.get("model", "openai"),
            tokens_used=result.get("tokens_used"),
            language=request.language,
        )

    async def enhance_prompt(self, request: EnhanceRequest) -> GenerateResponse:
        system_prompt = f"""You are a professional prompt engineer. Enhance the following prompt to make it more effective, clear, and detailed. 
Add structure, examples, and specific instructions where appropriate.
Language: {request.language}

Original prompt:
{request.prompt_content}

{request.instructions or "Improve clarity, add structure, and make it more effective."}"""

        result = await self._call_ai_api(system_prompt)
        return GenerateResponse(
            generated_content=result["content"],
            model=result.get("model", "openai"),
            language=request.language,
        )

    def _build_system_prompt(self, request: GenerateRequest) -> str:
        parts = [
            "You are a professional AI prompt engineer. Create a detailed, well-structured prompt.",
            f"Description: {request.description}",
            f"Language: {request.language}",
        ]
        if request.tone:
            parts.append(f"Tone: {request.tone}")
        if request.category_id:
            parts.append(f"Category: {request.category_id}")

        return "\n".join(parts)

    async def _call_ai_api(self, system_prompt: str, request: Optional[GenerateRequest] = None) -> dict:
        if not settings.openai_api_key:
            return self._get_fallback_response(system_prompt)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": system_prompt}],
                        "temperature": request.temperature if request else 0.7,
                        "max_tokens": 2000,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": "gpt-4",
                    "tokens_used": data["usage"]["total_tokens"],
                }
        except Exception:
            return self._get_fallback_response(system_prompt)

    def _get_fallback_response(self, prompt: str) -> dict:
        return {
            "content": f"# Generated Prompt\n\nBased on your request, here's a professional prompt:\n\n{prompt}\n\n---\n*This is a fallback response. Connect an AI API key for AI-powered generation.*",
            "model": "fallback",
            "tokens_used": 0,
        }

    async def _check_daily_limit(self, user_id: str) -> bool:
        from datetime import datetime, timezone, timedelta
        from sqlalchemy import select, func
        from app.models.log import UsageLog

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user_id,
            UsageLog.action == "generate",
            UsageLog.created_at >= today_start,
        )
        result = await self.session.execute(query)
        count = result.scalar() or 0
        return count < settings.free_daily_generations

    async def _log_generation(self, user_id: str) -> None:
        from app.models.log import UsageLog
        from datetime import datetime, timezone

        log = UsageLog(
            user_id=user_id,
            action="generate",
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(log)
        await self.session.flush()
