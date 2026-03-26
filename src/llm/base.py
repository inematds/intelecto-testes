from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], system: str = "") -> str:
        """Envia mensagens para o LLM e retorna a resposta como texto."""
        ...
