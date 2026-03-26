# Intelecto AI Framework — Relatório de Plano e Execução

**Data:** 2026-03-25

---

## 1. Visão Geral

Framework de agente IA customizado chamado "Intelecto", rodando inteiramente em Docker. Recebe mensagens via WhatsApp, processa com LLM (OpenRouter), e responde com personalidade configurável.

---

## 2. Decisões Técnicas

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Linguagem | Python 3.12 | Simplicidade, ecossistema IA maduro |
| Web framework | FastAPI | Async nativo, alta performance |
| WhatsApp | Evolution API | Open-source, roda em Docker, sem custo de API |
| LLM Provider | OpenRouter (primário) + Ollama (fallback) | 100+ modelos com uma chave, fallback local |
| DB memória | SQLite | Leve, sem container extra |
| DB vetorial | ChromaDB | Busca semântica, container dedicado |
| Scheduler | APScheduler | Integra com Python/SQLite nativamente |
| Orquestração | Docker Compose | Multi-container simples |

---

## 3. Arquitetura

```
docker-compose.yml
├── intelecto        (FastAPI app - core do agente)
├── evolution-api    (gateway WhatsApp)
├── chromadb         (busca semântica - Fase 4)
└── ollama           (fallback LLM local - Fase 4, opcional)
```

**Fluxo de mensagem:**
```
WhatsApp → Evolution API → webhook POST /webhook/whatsapp → FastAPI → OpenRouter → resposta → Evolution API → WhatsApp
```

---

## 4. Estrutura de Arquivos

```
intelecto-testes/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── soul.md
├── src/
│   ├── main.py                    # FastAPI app + webhook
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── agent/
│   │   ├── core.py                # Orquestrador do agente
│   │   ├── soul.py                # Loader do soul.md
│   │   └── compaction.py          # Auto-compaction (Fase 2)
│   ├── llm/
│   │   ├── base.py                # Interface abstrata LLMProvider
│   │   ├── openrouter.py          # Provider OpenRouter
│   │   └── ollama.py              # Provider Ollama (Fase 4)
│   ├── channels/
│   │   └── whatsapp.py            # Client Evolution API
│   ├── memory/
│   │   ├── store.py               # Two-layer memory (Fase 2)
│   │   └── solutions.py           # Solution memory (Fase 2)
│   ├── knowledge/
│   │   ├── indexer.py             # Indexação de docs (Fase 4)
│   │   └── search.py              # Busca semântica (Fase 4)
│   └── scheduler/
│       ├── cron.py                # Cron jobs (Fase 3)
│       └── heartbeat.py           # Check-in periódico (Fase 3)
├── data/
│   └── documents/
├── docs/
└── tests/
```

---

## 5. Fases de Implementação

### Fase 1 — Core Funcional (MVP) ✅ CONCLUÍDA

**Objetivo:** IA responde pelo WhatsApp usando OpenRouter.

**Arquivos criados:**
- `docker-compose.yml` — Containers intelecto + evolution-api
- `Dockerfile` — Python 3.12 slim com uvicorn
- `.env.example` — Variáveis de ambiente necessárias
- `requirements.txt` — fastapi, uvicorn, httpx, pydantic-settings
- `soul.md` — Personalidade padrão (PT-BR, informal, conciso)
- `src/config.py` — Configurações centralizadas via pydantic-settings
- `src/main.py` — FastAPI com endpoints `/health` e `/webhook/whatsapp`
- `src/agent/core.py` — Orquestrador: monta prompt (soul + histórico) → chama LLM → retorna resposta
- `src/agent/soul.py` — Carrega soul.md com cache
- `src/llm/base.py` — Interface abstrata `LLMProvider` com método `chat()`
- `src/llm/openrouter.py` — Implementação OpenRouter via httpx async
- `src/channels/whatsapp.py` — Client Evolution API: `send_text()` e `extract_message()`
- `.gitignore` — Ignora .env, __pycache__, data/memory.db

**Detalhes de implementação:**
- Histórico em memória (dict por remote_jid, máximo 20 mensagens)
- Ignora mensagens `fromMe` (do próprio bot)
- Suporta texto direto e extendedTextMessage (com preview de link)
- Tratamento de erro no LLM com mensagem amigável ao usuário
- Evolution API configurada com webhook global apontando para o container intelecto

**Como testar:**
1. Copiar `.env.example` para `.env` e preencher as chaves
2. `docker compose up --build`
3. Acessar `http://localhost:8080` para QR code do WhatsApp
4. Enviar mensagem — a IA responde com personalidade do soul.md

---

### Fase 2 — Memória (PENDENTE)

**Objetivo:** IA lembra de conversas e soluções anteriores.

**Funcionalidades planejadas:**
- **Two-layer memory (SQLite):**
  - Camada 1: Fatos rápidos (key-value)
  - Camada 2: Histórico pesquisável (full-text search)
- **Solution memory:** Salva soluções bem-sucedidas, busca por similaridade
- **Session auto-compaction:** Sumariza mensagens antigas quando histórico passa de N tokens
- Injetar contexto de memória no prompt do agente

---

### Fase 3 — Automação (PENDENTE)

**Objetivo:** IA executa tarefas agendadas e faz check-ins proativos.

**Funcionalidades planejadas:**
- **Cron scheduling (APScheduler):**
  - CRUD de jobs via mensagem WhatsApp ("me lembre toda segunda às 9h")
  - Persistência no SQLite
- **Heartbeat system:** A cada 30min verifica pendências e notifica

---

### Fase 4 — Knowledge Base + Ollama Fallback (PENDENTE)

**Objetivo:** IA pesquisa documentos e tem fallback local.

**Funcionalidades planejadas:**
- Adicionar containers ChromaDB e Ollama no docker-compose
- **Indexer:** Recebe PDFs/docs via WhatsApp, extrai texto, indexa no ChromaDB
- **RAG:** Busca trechos relevantes e injeta no prompt
- **Ollama provider:** Fallback automático quando OpenRouter falha

---

## 6. Variáveis de Ambiente

| Variável | Descrição | Fase |
|----------|-----------|------|
| `OPENROUTER_API_KEY` | Chave da API OpenRouter | 1 |
| `OPENROUTER_MODEL` | Modelo a usar (default: claude-sonnet) | 1 |
| `EVOLUTION_API_URL` | URL interna da Evolution API | 1 |
| `EVOLUTION_API_KEY` | Chave de autenticação da Evolution API | 1 |
| `EVOLUTION_INSTANCE_NAME` | Nome da instância WhatsApp | 1 |
| `LOG_LEVEL` | Nível de log (info, debug, etc) | 1 |
| `CHROMADB_URL` | URL do ChromaDB | 4 |
| `OLLAMA_URL` | URL do Ollama | 4 |

---

## 7. Verificação por Fase

| Fase | Teste |
|------|-------|
| 1 | `docker compose up` → conectar WhatsApp → enviar mensagem → receber resposta |
| 2 | Enviar várias mensagens → perguntar "o que conversamos?" → IA lembra |
| 3 | Dizer "me avise toda segunda às 9h" → job criado → executa no horário |
| 4 | Enviar PDF → perguntar sobre conteúdo → IA responde com base no documento |
