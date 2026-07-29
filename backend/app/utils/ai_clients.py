from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Optional

import httpx

from app.core.config import settings
from app.core.constants import AI_PROVIDERS


class BaseAIClient:
    provider: str = ""
    api_key: Optional[str] = None
    base_url: str = ""
    default_model: str = ""
    supports_streaming: bool = True

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        raise NotImplementedError

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        raise NotImplementedError
        yield ""

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=self._get_headers())
            if response.status_code == 401:
                raise PermissionError(f"{self.provider} API authentication failed. Check your API key.")
            if response.status_code == 429:
                raise RuntimeError(f"{self.provider} API rate limit exceeded.")
            response.raise_for_status()
            return response.json()

    async def _post_stream(
        self, url: str, payload: dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload, headers=self._get_headers()) as response:
                if response.status_code == 401:
                    raise PermissionError(f"{self.provider} API authentication failed.")
                if response.status_code == 429:
                    raise RuntimeError(f"{self.provider} API rate limit exceeded.")
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        if data_str:
                            try:
                                chunk = json.loads(data_str)
                                yield chunk
                            except json.JSONDecodeError:
                                continue


class AIClientFactory:
    @staticmethod
    def get_client(provider: str) -> BaseAIClient:
        clients: dict[str, type[BaseAIClient]] = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "google": GoogleClient,
            "deepseek": DeepSeekClient,
            "grok": GrokClient,
            "mistral": MistralClient,
            "perplexity": PerplexityClient,
            "qwen": QwenClient,
            "llama": LlamaClient,
        }
        client_class = clients.get(provider)
        if not client_class:
            raise ValueError(f"Unsupported AI provider: {provider}. Supported: {', '.join(clients.keys())}")
        return client_class()


class OpenAIClient(BaseAIClient):
    provider = "openai"
    base_url = "https://api.openai.com/v1"
    default_model = "gpt-4o"

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        if not self.api_key:
            self.api_key = ""

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "top_p": params.get("top_p", 1.0),
            "frequency_penalty": params.get("frequency_penalty", 0.0),
            "presence_penalty": params.get("presence_penalty", 0.0),
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})
        if params.get("stop"):
            payload["stop"] = params["stop"]

        data = await self._post(f"{self.base_url}/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        async for chunk in self._post_stream(f"{self.base_url}/chat/completions", payload):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content


class AnthropicClient(BaseAIClient):
    provider = "anthropic"
    base_url = "https://api.anthropic.com/v1"
    default_model = "claude-3-sonnet-20240229"

    def __init__(self) -> None:
        self.api_key = settings.anthropic_api_key
        if not self.api_key:
            self.api_key = ""

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
        }

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params.get("max_tokens", 2048),
            "temperature": params.get("temperature", 0.7),
        }
        if params.get("system_prompt"):
            payload["system"] = params["system_prompt"]

        data = await self._post(f"{self.base_url}/messages", payload)
        content = data.get("content", [])
        if isinstance(content, list):
            return "".join(block.get("text", "") for block in content if block.get("type") == "text")
        return str(content)

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/messages", json=payload, headers=self._get_headers()) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        if data_str:
                            try:
                                chunk = json.loads(data_str)
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        yield delta.get("text", "")
                            except json.JSONDecodeError:
                                continue


class DeepSeekClient(BaseAIClient):
    provider = "deepseek"
    base_url = "https://api.deepseek.com/v1"
    default_model = "deepseek-chat"

    def __init__(self) -> None:
        self.api_key = settings.deepseek_api_key
        if not self.api_key:
            self.api_key = ""

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        data = await self._post(f"{self.base_url}/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }

        async for chunk in self._post_stream(f"{self.base_url}/chat/completions", payload):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content


class GoogleClient(BaseAIClient):
    provider = "google"
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    default_model = "gemini-pro"

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            self.api_key = ""

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        model_name = model or self.default_model
        url = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": params.get("temperature", 0.7),
                "maxOutputTokens": params.get("max_tokens", 2048),
                "topP": params.get("top_p", 1.0),
            },
        }
        if params.get("system_prompt"):
            payload["systemInstruction"] = {"parts": [{"text": params["system_prompt"]}]}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts)

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        model_name = model or self.default_model
        url = f"{self.base_url}/models/{model_name}:streamGenerateContent?key={self.api_key}&alt=sse"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": params.get("temperature", 0.7),
                "maxOutputTokens": params.get("max_tokens", 2048),
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        candidates = chunk.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for p in parts:
                                if p.get("text"):
                                    yield p["text"]
                    except json.JSONDecodeError:
                        continue


class GrokClient(BaseAIClient):
    provider = "grok"
    base_url = "https://api.x.ai/v1"
    default_model = "grok-1"

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        if not self.api_key:
            self.api_key = ""

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        data = await self._post(f"{self.base_url}/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }

        async for chunk in self._post_stream(f"{self.base_url}/chat/completions", payload):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content


class MistralClient(BaseAIClient):
    provider = "mistral"
    base_url = "https://api.mistral.ai/v1"
    default_model = "mistral-large"

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        if not self.api_key:
            self.api_key = ""

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "top_p": params.get("top_p", 1.0),
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        data = await self._post(f"{self.base_url}/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }

        async for chunk in self._post_stream(f"{self.base_url}/chat/completions", payload):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content


class PerplexityClient(BaseAIClient):
    provider = "perplexity"
    base_url = "https://api.perplexity.ai"
    default_model = "pplx-7b-online"

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        if not self.api_key:
            self.api_key = ""

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        data = await self._post(f"{self.base_url}/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }

        async for chunk in self._post_stream(f"{self.base_url}/chat/completions", payload):
            choices = chunk.get("choices", [{}])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content


class QwenClient(BaseAIClient):
    provider = "qwen"
    base_url = "https://dashscope-intl.aliyuncs.com/api/v1"
    default_model = "qwen-max"

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        if not self.api_key:
            self.api_key = ""

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "input": {"messages": [{"role": "user", "content": prompt}]},
            "parameters": {
                "temperature": params.get("temperature", 0.7),
                "max_tokens": params.get("max_tokens", 2048),
            },
        }
        if params.get("system_prompt"):
            payload["input"]["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        data = await self._post(f"{self.base_url}/services/aigc/text-generation/generation", payload)
        output = data.get("output", {})
        return output.get("text", "")

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "input": {"messages": [{"role": "user", "content": prompt}]},
            "parameters": {
                "temperature": params.get("temperature", 0.7),
                "max_tokens": params.get("max_tokens", 2048),
                "incremental_output": True,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/services/aigc/text-generation/generation", json=payload, headers=self._get_headers()) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        output = chunk.get("output", {})
                        text = output.get("text", "")
                        if text:
                            yield text
                    except json.JSONDecodeError:
                        continue


class LlamaClient(BaseAIClient):
    provider = "llama"
    base_url = "https://api.together.xyz/v1"
    default_model = "meta-llama/Llama-3-70b-chat-hf"

    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        if not self.api_key:
            self.api_key = ""

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        if not self.api_key:
            return MockClient().generate(prompt, model, parameters)

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
        }
        if params.get("system_prompt"):
            payload["messages"].insert(0, {"role": "system", "content": params["system_prompt"]})

        data = await self._post(f"{self.base_url}/chat/completions", payload)
        return data["choices"][0]["message"]["content"]

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in MockClient().generate_stream(prompt, model, parameters):
                yield chunk
            return

        params = parameters or {}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 2048),
            "stream": True,
        }

        async for chunk in self._post_stream(f"{self.base_url}/chat/completions", payload):
            choices = chunk.get("choices", [{}])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content


class MockClient(BaseAIClient):
    provider = "mock"
    supports_streaming = True

    async def generate(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> str:
        return (
            f"This is a simulated response for your prompt.\n\n"
            f"Prompt received: {prompt[:100]}...\n\n"
            f"To enable real AI responses, configure an API key for one of the "
            f"supported providers in the environment settings."
        )

    async def generate_stream(self, prompt: str, model: Optional[str] = None, parameters: Optional[dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        words = (
            f"Here is a simulated streaming response for your prompt. "
            f"Prompt received: {prompt[:80]}... "
            f"To enable real AI responses, configure an API key."
        ).split()
        for word in words:
            yield word + " "
