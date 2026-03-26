import logging

import httpx

from src.config import settings
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(LLMProvider):
    def __init__(self) -> None:
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model

    async def chat(self, messages: list[dict], system: str = "") -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "model": self.model,
            "messages": messages,
        }

        if system:
            payload["messages"] = [{"role": "system", "content": system}, *messages]

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        logger.info("OpenRouter response: model=%s, tokens=%s", self.model, data.get("usage"))
        return content
