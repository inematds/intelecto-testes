# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Intelecto is a custom AI agent framework that runs in Docker. It connects to WhatsApp via Evolution API, uses OpenRouter for LLM calls, and will support memory, scheduling, and document knowledge base.

## Stack

- **Python 3.12** + **FastAPI** + **uvicorn**
- **Evolution API** (WhatsApp gateway, separate container)
- **OpenRouter** (LLM provider, with Ollama as future fallback)
- **SQLite** (memory/history, Fase 2)
- **ChromaDB** (vector search for documents, Fase 4)
- **Docker Compose** for orchestration

## Commands

```bash
# Run everything
docker compose up --build

# Run just the app (dev, outside Docker)
uvicorn src.main:app --reload --port 8000

# Rebuild after code changes
docker compose up --build intelecto
```

## Architecture

```
WhatsApp → Evolution API → POST /webhook/whatsapp → FastAPI → OpenRouter → resposta → Evolution API → WhatsApp
```

Key modules:
- `src/main.py` — FastAPI app, webhook endpoint
- `src/agent/core.py` — Agent orchestrator (builds prompt with soul + history, calls LLM)
- `src/agent/soul.py` — Loads `soul.md` personality file
- `src/llm/base.py` — Abstract LLM provider interface
- `src/llm/openrouter.py` — OpenRouter implementation
- `src/channels/whatsapp.py` — Evolution API client (send/receive)

## Implementation Phases

- **Fase 1** (done): Core MVP — WhatsApp + OpenRouter + soul.md
- **Fase 2** (todo): Memory — SQLite two-layer memory, solution memory, session compaction
- **Fase 3** (todo): Automation — Cron scheduling (APScheduler), heartbeat system
- **Fase 4** (todo): Knowledge base (ChromaDB RAG) + Ollama fallback

## Config

All config via environment variables (`.env` file). See `.env.example` for required vars. Uses `pydantic-settings` in `src/config.py`.

## Notes

- The spec (`my-framework-ingredients (5).md`) is written in Portuguese/English mix
- `soul.md` at project root defines the AI personality — mounted read-only into the container
- Session history is currently in-memory (dict per remote_jid), will move to SQLite in Fase 2
