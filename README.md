# Intelecto

Agente de IA conectado ao WhatsApp via Evolution API, com LLM via OpenRouter.

```
WhatsApp → Evolution API → FastAPI (webhook) → OpenRouter (LLM) → resposta → Evolution API → WhatsApp
```

## Pré-requisitos

- Docker e Docker Compose instalados
- Chave de API do [OpenRouter](https://openrouter.ai/)
- Um número de WhatsApp para conectar ao bot

## Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd intelecto-testes
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `OPENROUTER_API_KEY` | Chave da API do OpenRouter | `sk-or-v1-xxxx` |
| `OPENROUTER_MODEL` | Modelo LLM a utilizar | `anthropic/claude-sonnet-4-20250514` |
| `EVOLUTION_API_URL` | URL interna da Evolution API | `http://evolution-api:8080` |
| `EVOLUTION_API_KEY` | Chave de autenticação da Evolution API | `minha-chave-secreta` |
| `EVOLUTION_INSTANCE_NAME` | Nome da instância do WhatsApp | `intelecto` |
| `LOG_LEVEL` | Nível de log | `info` |

### 3. Personalidade do agente

O arquivo `soul.md` na raiz do projeto define a personalidade do agente. Edite conforme desejado antes de subir.

## Subindo o sistema

```bash
docker compose up --build
```

Isso inicia dois containers:

| Container | Porta | Descrição |
|-----------|-------|-----------|
| **intelecto** | 8000 | App FastAPI (webhook + API) |
| **evolution-api** | 8085 | Gateway WhatsApp (Evolution API v1.8.0) |

Para rodar em background:

```bash
docker compose up --build -d
```

Para reconstruir apenas o app após mudanças no código:

```bash
docker compose up --build intelecto -d
```

## Conectando o WhatsApp

### 1. Criar a instância na Evolution API

Acesse o painel da Evolution API em `http://localhost:8085` ou crie via API:

```bash
curl -X POST http://localhost:8085/instance/create \
  -H "apikey: SUA_EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "intelecto",
    "qrcode": true
  }'
```

A resposta inclui um QR Code em base64. Você também pode acessar o QR Code pelo painel web.

### 2. Escanear o QR Code

Abra o WhatsApp no celular:
1. Vá em **Configurações > Aparelhos conectados**
2. Toque em **Conectar um aparelho**
3. Escaneie o QR Code gerado

### 3. Verificar conexão

```bash
curl -H "apikey: SUA_EVOLUTION_API_KEY" \
  http://localhost:8085/instance/connectionState/intelecto
```

O status deve ser `"open"` quando conectado.

### 4. Webhook (automático)

O Intelecto configura o webhook automaticamente ao iniciar. Ele verifica se a instância existe e se o webhook está apontando para `http://intelecto:8000/webhook/whatsapp`. Se não estiver, configura sozinho.

Caso precise configurar manualmente:

```bash
curl -X POST http://localhost:8085/webhook/set/intelecto \
  -H "apikey: SUA_EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "http://intelecto:8000/webhook/whatsapp",
    "webhook_by_events": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

## Verificando se está tudo funcionando

### Status dos containers

```bash
docker compose ps
```

### Logs do Intelecto

```bash
docker compose logs -f intelecto
```

### Teste rápido

Envie uma mensagem para o número do WhatsApp conectado. Nos logs do Intelecto você deve ver:

```
INFO src.main: Mensagem de <remetente>: <texto>
INFO httpx: HTTP Request: POST https://openrouter.ai/api/v1/chat/completions "HTTP/1.1 200 OK"
INFO src.channels.whatsapp: Mensagem enviada para <destinatario>
```

## Desenvolvimento local (sem Docker)

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

Neste caso, ajuste `EVOLUTION_API_URL` no `.env` para apontar para a URL acessível da Evolution API (ex: `http://localhost:8085`).

## Estrutura do projeto

```
├── docker-compose.yml    # Orquestração dos containers
├── Dockerfile            # Build do app Python
├── .env                  # Variáveis de ambiente (não commitado)
├── .env.example          # Template das variáveis
├── soul.md               # Personalidade do agente
├── requirements.txt      # Dependências Python
├── data/                 # Dados persistentes (lid_map.json, etc)
└── src/
    ├── main.py           # FastAPI app, webhook, lifespan
    ├── config.py         # Configurações (pydantic-settings)
    ├── agent/
    │   ├── core.py       # Orquestrador do agente
    │   └── soul.py       # Carrega soul.md
    ├── channels/
    │   └── whatsapp.py   # Cliente Evolution API (envio/recebimento)
    └── llm/
        ├── base.py       # Interface abstrata do LLM
        └── openrouter.py # Implementação OpenRouter
```

## Troubleshooting

### Mensagens não chegam no bot
- Verifique se a instância está conectada (`connectionState` = `open`)
- Verifique os logs: `docker compose logs -f intelecto`
- O webhook é configurado automaticamente, mas confirme com:
  ```bash
  curl -H "apikey: SUA_EVOLUTION_API_KEY" http://localhost:8085/webhook/find/intelecto
  ```

### Bot recebe mas não responde
- Verifique os logs por erros na chamada ao OpenRouter
- Confirme que `OPENROUTER_API_KEY` está válida no `.env`
- Verifique se o mapeamento LID existe em `data/lid_map.json`

### Instância perdida após restart
- A Evolution API persiste instâncias nos volumes Docker (`evolution_instances`, `evolution_store`)
- Se os volumes forem removidos, é necessário recriar a instância e escanear o QR Code novamente
- O webhook será reconfigurado automaticamente pelo Intelecto

## Guia Rápido

```bash
# 1. Clonar e configurar
git clone git@github.com:inematds/intelecto-testes.git
cd intelecto-testes
cp .env.example .env
# Edite o .env com suas chaves

# 2. Subir os containers
docker compose up --build -d

# 3. Acessar o painel da Evolution API
# Abra http://localhost:8085 no navegador
# Crie a instância com o nome "intelecto"
# Escaneie o QR Code no WhatsApp (Configurações > Aparelhos conectados)

# 4. Pronto! Mande uma mensagem no WhatsApp e o bot responde.

# Comandos úteis:
docker compose logs -f intelecto   # Ver logs
docker compose restart intelecto   # Reiniciar após trocar .env
docker compose down                # Parar tudo
```
