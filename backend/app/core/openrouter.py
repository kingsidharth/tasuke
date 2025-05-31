import openai
from typing import List, Dict, Any, AsyncIterator
import os
from backend.app.core.logging import logger

class OpenRouterClient:
    """OpenRouter client for LLM interactions."""
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.default_model = "anthropic/claude-3-haiku"
        self.headers = {
            "HTTP-Referer": "https://tasuke.local",
            "X-Title": "Tasuke AI Agent Platform"
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict] = None,
        model: str = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            params = {
                "model": model or self.default_model,
                "messages": messages,
                "stream": stream,
                "extra_headers": self.headers,
                **kwargs
            }
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            logger.info("OpenRouter request", model=params["model"], message_count=len(messages))
            response = await self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            logger.error("OpenRouter API error", error=str(e), model=model or self.default_model)
            raise

openrouter_client = OpenRouterClient() 