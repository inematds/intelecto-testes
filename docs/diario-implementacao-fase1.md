# Diário de Implementação — Fase 1 (Core MVP)

**Data:** 2026-03-25
**Objetivo:** IA respondendo pelo WhatsApp usando OpenRouter

---

## 1. Setup Inicial

Criados todos os arquivos base do projeto:
- `Dockerfile` (Python 3.12 slim + FastAPI + uvicorn)
- `docker-compose.yml`
- `src/main.py` — FastAPI com webhook `/webhook/whatsapp`
- `src/agent/core.py` — Orquestrador do agente (soul + histórico → LLM)
- `src/agent/soul.py` — Loader do `soul.md` com cache
- `src/llm/base.py` — Interface abstrata `LLMProvider`
- `src/llm/openrouter.py` — Provider OpenRouter via httpx async
- `src/channels/whatsapp.py` — Client Evolution API
- `src/config.py` — Settings via pydantic-settings
- `soul.md` — Personalidade padrão em PT-BR
- `.env.example` — Template de variáveis de ambiente

O container `intelecto` (FastAPI) buildou e subiu sem problemas na primeira tentativa.

---

## 2. Problema: Porta 8080 já em uso

**Erro:**
```
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Causa:** Outro serviço na máquina já usava a porta 8080.

**Solução:** Mapeei a porta externa para `8085`:
```yaml
ports:
  - "8085:8080"  # era "8080:8080"
```

---

## 3. Problema: Evolution API v2.2.3 — "Database provider invalid"

**Erro:**
```
Error: Database provider  invalid.
```
O container reiniciava em loop.

**Causa:** A v2.x da Evolution API exige um banco de dados configurado (PostgreSQL).

**Solução:** Adicionei um container PostgreSQL e as variáveis:
```yaml
evolution-db:
  image: postgres:16-alpine
  environment:
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres
    - POSTGRES_DB=evolution

evolution-api:
  environment:
    - DATABASE_PROVIDER=postgresql
    - DATABASE_CONNECTION_URI=postgresql://postgres:postgres@evolution-db:5432/evolution
```

---

## 4. Problema: Evolution API v2.2.3 — QR Code nunca é gerado

**Erro:** O endpoint `GET /instance/connect/{instance}` sempre retornava `{"count": 0}` sem gerar QR code nem pairing code. Testado com múltiplas tentativas, delays de até 15 segundos, recriação de instância.

**Investigação:**
- A API respondia normalmente a outros endpoints (create, fetchInstances, connectionState)
- O container alcançava o WhatsApp (`https://web.whatsapp.com` retornava 200)
- Logs mostravam **"redis disconnected"** em loop — a v2.2.3 precisa de Redis para o Baileys funcionar
- Mesmo adicionando Redis ao docker-compose, o QR continuou não sendo gerado
- O problema persistiu nas versões v2.2.3 e v2.1.1

**Conclusão:** A v2.x tem dependências complexas (PostgreSQL + Redis) e o Baileys não conseguia iniciar o handshake WebSocket com o WhatsApp, provavelmente por configuração faltante não documentada.

**Solução:** Voltei para a **v1.8.0** que:
- Não precisa de PostgreSQL (usa arquivos locais)
- Não precisa de Redis
- Gera QR code imediatamente no `POST /instance/create` com `qrcode: true`

```yaml
evolution-api:
  image: atendai/evolution-api:v1.8.0
```

O QR code foi gerado com sucesso na primeira tentativa com v1.8.0.

---

## 5. Problema: Formato do payload sendText (v1.8.0)

**Erro:**
```
httpx.HTTPStatusError: Client error '400 Bad Request' for url '.../message/sendText/intelecto'
```

**Causa:** O formato do payload mudou entre versões:
- v2.x usa: `{"number": "...", "text": "..."}`
- v1.8.0 usa: `{"number": "...", "textMessage": {"text": "..."}}`

**Solução:** Atualizei `whatsapp.py`:
```python
# Antes (v2.x)
payload = {"number": remote_jid, "text": text}

# Depois (v1.8.0)
payload = {"number": remote_jid, "textMessage": {"text": text}}
```

---

## 6. Problema: Formato LID do WhatsApp (o mais complexo)

**Erro:**
```
{"status":400,"error":"Bad Request","response":{"message":[{"exists":false,"jid":"46231128641703@lid"}]}}
```

**Causa:** O WhatsApp mudou o formato de identificação de usuários. Antes usava o número de telefone (`555194036619@s.whatsapp.net`), agora usa um ID interno chamado **LID** (`46231128641703@lid`). O webhook da Evolution API v1.8.0 envia o `remoteJid` no formato LID, mas o endpoint `sendText` **não aceita LID** — precisa do número real.

**Investigação:**
- O campo `participant` no webhook vem `null` para chats 1:1
- O campo `sender` no body raiz é o número do **bot**, não do remetente
- Não há campo no webhook que contenha o número real do remetente
- A API de contatos (`chat/findContacts`) retorna todos os contatos com número real + pushName

**Solução implementada — mapeamento LID → número:**

1. Adicionei um cache em memória `_lid_to_number: dict[str, str]` em `whatsapp.py`
2. Criado endpoint `POST /map-lid` para registrar mapeamentos manualmente
3. No `send_text()`, quando o `remote_jid` contém `@lid`, busca o número real no cache
4. Busquei o número pelo `pushName` na API de contatos:
   - `pushName: "Nei Eugênio Maldaner"` → `555194036619@s.whatsapp.net`
5. Registrei o mapeamento via curl:
```bash
curl -X POST http://localhost:8000/map-lid \
  -H "Content-Type: application/json" \
  -d '{"lid":"46231128641703@lid","number":"555194036619@s.whatsapp.net"}'
```

**Limitação:** O mapeamento é em memória — se o container reiniciar, precisa registrar novamente. Será resolvido na Fase 2 quando a memória for persistida em SQLite.

**Solução futura (Fase 2):** Automatizar o mapeamento no startup buscando todos os contatos e correlacionando com mensagens recentes via pushName.

---

## 7. Problema: Webhook não configurado na instância

**Erro:** Mensagens chegavam ao WhatsApp mas não ao FastAPI.

**Causa:** A variável `WEBHOOK_GLOBAL_URL` no docker-compose nem sempre é respeitada pela v1.8.0. O webhook precisa ser configurado explicitamente na instância.

**Solução:** Configurar webhook via API após criar a instância:
```bash
curl -X POST http://localhost:8085/webhook/set/intelecto \
  -H "apikey: meutesteintelecto" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "http://intelecto:8000/webhook/whatsapp",
    "webhook_by_events": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

## 8. Problema: Formato do evento no webhook

**Erro:** Webhook recebia eventos mas ignorava todos.

**Causa:** O código original filtrava por `event == "messages.upsert"` (exato), mas dependendo da versão o evento pode variar.

**Solução:** Mudei para verificação mais flexível:
```python
# Antes
if event != "messages.upsert":

# Depois
if "messages" not in event:
```

---

## 9. Problema: QR Code expira rápido

**Observação:** O QR code gerado pela Evolution API expira em ~45 segundos. Se o usuário não escanear a tempo, precisa gerar outro via `GET /instance/connect/{instance}`.

**Aprendizado:** Sempre verificar `GET /instance/connectionState/{instance}` antes de tentar gerar novo QR. Se já estiver `open`, não precisa reconectar.

---

## 10. Problema: Sessão WhatsApp persistida nos volumes

**Observação (positiva):** Ao reiniciar os containers, a conexão WhatsApp é mantida se os volumes Docker forem preservados (`evolution_instances`, `evolution_store`). Não precisa escanear QR novamente.

**Cuidado:** Ao fazer `docker compose down -v` (com `-v`), os volumes são deletados e a sessão é perdida — precisará reconectar via QR.

---

## Configuração Final que Funciona

### docker-compose.yml
```yaml
services:
  intelecto:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./soul.md:/app/soul.md:ro
    depends_on: [evolution-api]

  evolution-api:
    image: atendai/evolution-api:v1.8.0
    ports: ["8085:8080"]
    environment:
      - AUTHENTICATION_TYPE=apikey
      - AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY}
      - QRCODE_LIMIT=30
      - CONFIG_SESSION_PHONE_CLIENT=Intelecto
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store
```

### Passos para conectar WhatsApp
```bash
# 1. Criar instância com QR
curl -X POST http://localhost:8085/instance/create \
  -H "apikey: SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"instanceName":"intelecto","qrcode":true}'
# Salva o QR code base64 retornado e escaneia

# 2. Configurar webhook
curl -X POST http://localhost:8085/webhook/set/intelecto \
  -H "apikey: SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"url":"http://intelecto:8000/webhook/whatsapp","webhook_by_events":false,"events":["MESSAGES_UPSERT"]}'

# 3. Registrar mapeamento LID (necessário para cada contato que enviar mensagem)
curl -X POST http://localhost:8000/map-lid \
  -H "Content-Type: application/json" \
  -d '{"lid":"ID_LID@lid","number":"NUMERO@s.whatsapp.net"}'
```

### Fluxo completo funcionando
```
WhatsApp (msg) → Evolution API v1.8.0 → webhook POST → FastAPI
  → extract_message() extrai LID + texto
  → handle_message() monta prompt (soul.md + histórico) → OpenRouter (Claude Sonnet)
  → send_text() mapeia LID → número real → Evolution API → WhatsApp (resposta)
```

---

## Lições Aprendidas

1. **Evolution API v2.x é instável para QR code** — precisa de PostgreSQL + Redis e mesmo assim pode não funcionar. A v1.8.0 é muito mais simples e confiável.

2. **O WhatsApp migrou para formato LID** — o `remoteJid` não é mais o número de telefone. Qualquer integração precisa lidar com isso. A v1.8.0 não suporta envio para LID, então é necessário um mapeamento LID→número.

3. **Volumes Docker preservam a sessão WhatsApp** — não use `docker compose down -v` a menos que queira reconectar.

4. **O webhook global do docker-compose nem sempre funciona** — configure explicitamente via API após criar a instância.

5. **Formatos de API mudam entre versões** — `sendText` usa payloads diferentes na v1.8.0 vs v2.x. Sempre teste o endpoint manualmente com `curl` antes de codificar.
