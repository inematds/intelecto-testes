import json
import logging
from pathlib import Path

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

# Persistência do mapeamento LID -> número real do telefone
_LID_MAP_FILE = Path("data/lid_map.json")
_lid_to_number: dict[str, str] = {}


def _load_lid_map() -> None:
    """Carrega mapeamento LID do disco."""
    global _lid_to_number
    if _LID_MAP_FILE.exists():
        try:
            _lid_to_number = json.loads(_LID_MAP_FILE.read_text())
            logger.info("Mapeamento LID carregado: %d entradas", len(_lid_to_number))
        except Exception:
            logger.warning("Falha ao carregar lid_map.json, iniciando vazio")
            _lid_to_number = {}


def _save_lid_map() -> None:
    """Salva mapeamento LID no disco."""
    try:
        _LID_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
        _LID_MAP_FILE.write_text(json.dumps(_lid_to_number, indent=2))
    except Exception:
        logger.warning("Falha ao salvar lid_map.json")


# Carrega ao importar o módulo
_load_lid_map()


async def send_text(remote_jid: str, text: str) -> None:
    """Envia mensagem de texto via Evolution API v1.8.0."""
    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance_name}"
    headers = {"apikey": settings.evolution_api_key, "Content-Type": "application/json"}

    # Se é LID, tenta usar o número real mapeado
    number = remote_jid
    if "@lid" in remote_jid:
        mapped = _lid_to_number.get(remote_jid)
        if mapped:
            number = mapped
            logger.info("LID %s mapeado para %s", remote_jid, mapped)
        else:
            logger.error("Número não mapeado para LID %s - não é possível enviar", remote_jid)
            return

    payload = {
        "number": number,
        "textMessage": {"text": text},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 400:
            logger.error("Falha ao enviar para %s: %s", number, resp.text[:200])
            return
        resp.raise_for_status()

    logger.info("Mensagem enviada para %s", number)


def extract_message(body: dict) -> tuple[str | None, str | None]:
    """Extrai remetente e texto de um webhook da Evolution API v1.8.0.

    Retorna (remote_jid, text) ou (None, None) se não for mensagem de texto.
    Também mapeia LID -> número real quando possível.
    """
    data = body.get("data", body)

    # Ignora mensagens enviadas pelo próprio bot
    if data.get("key", {}).get("fromMe", False):
        return None, None

    remote_jid = data.get("key", {}).get("remoteJid")

    # Mapeia LID -> número real usando o pushName + contatos
    # O webhook v1.8.0 tem 'sender' no nível raiz = número do bot
    # Mas podemos usar o 'source' e 'pushName' para buscar
    if remote_jid and "@lid" in remote_jid:
        # Tenta extrair número do participant ou de outros campos
        participant = data.get("participant")
        if participant and "@s.whatsapp.net" in participant:
            _lid_to_number[remote_jid] = participant
            _save_lid_map()

    # Texto direto
    text = data.get("message", {}).get("conversation")

    # Texto em mensagem extendida
    if not text:
        text = data.get("message", {}).get("extendedTextMessage", {}).get("text")

    if not remote_jid or not text:
        return None, None

    return remote_jid, text


def register_lid_mapping(lid: str, phone_number: str) -> None:
    """Registra manualmente um mapeamento LID -> número."""
    _lid_to_number[lid] = phone_number
    _save_lid_map()
    logger.info("Mapeamento registrado: %s -> %s", lid, phone_number)
