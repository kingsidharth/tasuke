import openai
from typing import List, Dict, Any, AsyncIterator
import os
from backend.app.core.logging import logger
from backend.app.core.config import settings
from loguru import logger as openrouter_logger

class OpenRouterClient:
    """OpenRouter client for LLM interactions."""
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.headers = {
            "HTTP-Referer": "https://tasuke.local",
            "X-Title": "Tasuke AI Agent Platform"
        }
        openrouter_logger.add("logs/openrouter.log", rotation="00:00", retention="90 days", level="INFO", serialize=False)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict] = None,
        model: str = None,
        temperature: float = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            params = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "extra_headers": self.headers,
                **kwargs
            }
            if temperature is not None:
                params["temperature"] = temperature
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            openrouter_logger.info("OpenRouter call", model=params["model"], message_count=len(messages), tools=tools)
            response = await self.client.chat.completions.create(**params)
            openrouter_logger.info("OpenRouter response", model=params["model"], response=str(response))
            return response
        except Exception as e:
            openrouter_logger.error("OpenRouter API error", error=str(e), model=model)
            logger.error("OpenRouter API error", error=str(e), model=model)
            raise

openrouter_client = OpenRouterClient() 