AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "supports_streaming": True,
        "docs_url": "https://platform.openai.com/docs",
    },
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "supports_streaming": True,
        "docs_url": "https://docs.anthropic.com",
    },
    "google": {
        "name": "Google Gemini",
        "models": ["gemini-pro", "gemini-ultra"],
        "supports_streaming": True,
        "docs_url": "https://ai.google.dev/docs",
    },
    "grok": {
        "name": "Grok",
        "models": ["grok-1"],
        "supports_streaming": True,
        "docs_url": "https://docs.x.ai",
    },
    "deepseek": {
        "name": "DeepSeek",
        "models": ["deepseek-chat", "deepseek-coder"],
        "supports_streaming": True,
        "docs_url": "https://platform.deepseek.com/docs",
    },
    "qwen": {
        "name": "Qwen",
        "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
        "supports_streaming": True,
        "docs_url": "https://help.aliyun.com/document_detail/2712195.html",
    },
    "llama": {
        "name": "Meta Llama",
        "models": ["llama-3-70b", "llama-3-8b"],
        "supports_streaming": True,
        "docs_url": "https://llama.meta.com/docs",
    },
    "mistral": {
        "name": "Mistral",
        "models": ["mistral-large", "mistral-medium", "mistral-small"],
        "supports_streaming": True,
        "docs_url": "https://docs.mistral.ai",
    },
    "perplexity": {
        "name": "Perplexity",
        "models": ["pplx-7b-online", "pplx-70b-online"],
        "supports_streaming": True,
        "docs_url": "https://docs.perplexity.ai",
    },
    "copilot": {
        "name": "GitHub Copilot",
        "models": ["copilot-chat"],
        "supports_streaming": False,
        "docs_url": "https://docs.github.com/copilot",
    },
}

PROMPT_CATEGORIES = [
    "code-generation",
    "code-review",
    "debugging",
    "explanation",
    "documentation",
    "creative-writing",
    "business",
    "education",
    "marketing",
    "data-analysis",
    "translation",
    "summarization",
    "role-playing",
    "brainstorming",
    "planning",
    "interview",
    "research",
    "technical-support",
    "customer-support",
    "healthcare",
    "legal",
    "finance",
    "science",
    "engineering",
]

PROMPT_TEMPLATE_VARIABLES = {
    "{{input}}": "User input text",
    "{{language}}": "Target programming language",
    "{{framework}}": "Target framework",
    "{{context}}": "Additional context",
    "{{tone}}": "Response tone (formal/casual)",
    "{{length}}": "Response length (short/medium/long)",
    "{{format}}": "Output format",
    "{{audience}}": "Target audience",
    "{{goal}}": "Specific goal or objective",
    "{{constraints}}": "Specific constraints or requirements",
}

STAR_THRESHOLDS = {
    1: 4.0,
    2: 4.5,
}

MAX_CACHE_SIZE_MB = 100
