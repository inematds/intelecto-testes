import logging

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request

from src.agent.core import handle_message
from src.channels.whatsapp import extract_message, send_text, register_lid_mapping
from src.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def ensure_webhook() -> None:
    """Garante que o webhook está configurado na instância da Evolution API."""
    instance = settings.evolution_instance_name
    base = settings.evolution_api_url
    headers = {"apikey": settings.evolution_api_key, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Verifica se a instância existe
            resp = await client.get(f"{base}/instance/connectionState/{instance}", headers=headers)
            if resp.status_code == 404:
                logger.warning("Instância '%s' não existe na Evolution API", instance)
                return

            # Verifica webhook atual
            resp = await client.get(f"{base}/webhook/find/{instance}", headers=headers)
            current = resp.json() if resp.status_code == 200 else {}

            webhook_url = f"http://intelecto:8000/webhook/whatsapp"

            # Configura se não estiver ativo ou URL diferente
            if not current or not current.get("enabled") or current.get("url") != webhook_url:
                resp = await client.post(f"{base}/webhook/set/{instance}", headers=headers, json={
                    "enabled": True,
                    "url": webhook_url,
                    "webhook_by_events": False,
                    "events": ["MESSAGES_UPSERT"],
                })
                if resp.status_code in (200, 201):
                    logger.info("Webhook configurado automaticamente para %s", webhook_url)
                else:
                    logger.warning("Falha ao configurar webhook: %s", resp.text[:200])
            else:
                logger.info("Webhook já configurado corretamente")
    except Exception as e:
        logger.warning("Não foi possível configurar webhook: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_webhook()
    yield


app = FastAPI(title="Intelecto", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    body = await request.json()
    event = body.get("event", "")

    # Processa apenas eventos de mensagem recebida
    if "messages" not in event:
        return {"status": "ignored"}

    remote_jid, text = extract_message(body)
    if not remote_jid or not text:
        return {"status": "ignored"}

    logger.info("Mensagem de %s: %s", remote_jid, text[:100])

    response = await handle_message(remote_jid, text)
    await send_text(remote_jid, response)

    return {"status": "ok"}


@app.post("/map-lid")
async def map_lid(request: Request):
    """Endpoint para registrar manualmente mapeamento LID -> número.
    Body: {"lid": "123@lid", "number": "5551999999999@s.whatsapp.net"}
    """
    data = await request.json()
    lid = data.get("lid")
    number = data.get("number")
    if lid and number:
        register_lid_mapping(lid, number)
        return {"status": "ok", "mapped": f"{lid} -> {number}"}
    return {"status": "error", "message": "lid and number required"}
