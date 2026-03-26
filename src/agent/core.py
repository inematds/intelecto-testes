import logging

from src.agent.soul import load_soul
from src.config import settings
from src.llm.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

_provider = OpenRouterProvider()

# Histórico em memória por conversa (será substituído pelo SQLite na Fase 2)
_sessions: dict[str, list[dict]] = {}

MAX_HISTORY = 20  # Máximo de mensagens no histórico por sessão


async def handle_message(remote_jid: str, text: str) -> str:
    """Processa uma mensagem do usuário e retorna a resposta da IA."""
    soul = load_soul(settings.soul_path)

    # Recupera ou cria histórico da sessão
    history = _sessions.setdefault(remote_jid, [])
    history.append({"role": "user", "content": text})

    # Limita tamanho do histórico
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    try:
        response = await _provider.chat(messages=history, system=soul)
    except Exception:
        logger.exception("Erro ao chamar LLM para %s", remote_jid)
        return "Desculpe, tive um problema ao processar sua mensagem. Tente novamente."

    history.append({"role": "assistant", "content": response})
    return response
