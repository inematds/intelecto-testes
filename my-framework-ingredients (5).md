# My Custom AI Framework - Ingredient List

> **Purpose**: This document defines the selected features, skills, and architectural patterns
> for building a custom AI agent framework. Each item includes a description of what it does,
> which reference frameworks implement it, and enough context for Claude Code to understand
> the implementation requirements.
>
> **Reference repos**: Located at `/Users/marwankashef/Desktop/YouTube/OpenClaw Antidote/`
> **Full analysis**: See `FRAMEWORK-DEEP-DIVE.md` in the same directory.

---

**Total selected items: 9**

## Identidade e Personalidade

### 1. Soul.md Personality File

**What it does**: Defina a personalidade, os valores e o estilo de comunicação da sua IA em um arquivo de texto simples. Como escrever uma ficha de personagem.

**Reference implementations**: OpenClaw, NanoBot, ZeroClaw, PicoClaw

**Where to find reference code**:
- OpenClaw (`./openclaw/`): TypeScript, check `skills/` and `extensions/` directories
- ZeroClaw (`./zeroclaw/`): Rust trait-based, check `src/tools/` directory
- NanoBot (`./nanobot/`): Python, check `nanobot/skills/` and `nanobot/agent/tools/`
- PicoClaw (`./picoclaw/`): Go, check `workspace/skills/` and `pkg/tools/`

---

## Canais de Comunicação

### 1. WhatsApp Integration

**What it does**: Converse com sua IA pelo WhatsApp. Envie mensagens, imagens, notas de voz. O mais natural para uso empresarial diário.

**Reference implementations**: OpenClaw, NanoClaw, NanoBot, PicoClaw, ZeroClaw, TinyClaw

**Where to find reference code**:
- OpenClaw (`./openclaw/`): TypeScript, check `skills/` and `extensions/` directories
- ZeroClaw (`./zeroclaw/`): Rust trait-based, check `src/tools/` directory
- NanoClaw (`./nanoclaw/`): TypeScript 5.2K lines, check `.claude/skills/` and `container/skills/`
- NanoBot (`./nanobot/`): Python, check `nanobot/skills/` and `nanobot/agent/tools/`
- PicoClaw (`./picoclaw/`): Go, check `workspace/skills/` and `pkg/tools/`
- TinyClaw (`./tinyclaw/`): TS/Bash, check `.agents/skills/` directory

---

## Memória e Conhecimento

### 1. Solution Memory

**What it does**: A IA salva automaticamente soluções bem-sucedidas. Na próxima vez que enfrentar um problema semelhante, ela se lembrará do que funcionou antes.

**Reference implementations**: Agent Zero

**Where to find reference code**:
- Agent Zero (`./agent-zero/`): Python, check `python/tools/` and `python/extensions/`

---

### 2. Two-Layer Memory

**What it does**: Camada 1: Fatos rápidos (MEMORY.md). Camada 2: Log de histórico pesquisável. Simples, mas eficaz.

**Reference implementations**: NanoBot, PicoClaw

**Where to find reference code**:
- NanoBot (`./nanobot/`): Python, check `nanobot/skills/` and `nanobot/agent/tools/`
- PicoClaw (`./picoclaw/`): Go, check `workspace/skills/` and `pkg/tools/`

---

### 3. Document Knowledge Base

**What it does**: Faça upload de PDFs, planilhas, documentos. A IA pode pesquisar e analisá-los. O conhecimento da sua empresa ao alcance da mão.

**Reference implementations**: Agent Zero, OpenClaw

**Where to find reference code**:
- OpenClaw (`./openclaw/`): TypeScript, check `skills/` and `extensions/` directories
- Agent Zero (`./agent-zero/`): Python, check `python/tools/` and `python/extensions/`

---

### 4. Session Auto-Compaction

**What it does**: Quando as conversas ficam muito longas, resume automaticamente as partes antigas para manter a IA rápida enquanto preserva informações essenciais.

**Reference implementations**: NanoClaw, IronClaw

**Where to find reference code**:
- NanoClaw (`./nanoclaw/`): TypeScript 5.2K lines, check `.claude/skills/` and `container/skills/`
- IronClaw (`./ironclaw/`): Rust + WASM, check `src/tools/builtin/` and `tools-src/`

---

## Automação e Agendamento

### 1. Cron Scheduling

**What it does**: Execute tarefas em um cronograma: "toda segunda-feira às 9h, me envie um briefing." Funciona como um despertador confiável para sua IA.

**Reference implementations**: OpenClaw, NanoClaw, NanoBot, PicoClaw, ZeroClaw, TinyClaw, IronClaw

**Where to find reference code**:
- OpenClaw (`./openclaw/`): TypeScript, check `skills/` and `extensions/` directories
- ZeroClaw (`./zeroclaw/`): Rust trait-based, check `src/tools/` directory
- NanoClaw (`./nanoclaw/`): TypeScript 5.2K lines, check `.claude/skills/` and `container/skills/`
- NanoBot (`./nanobot/`): Python, check `nanobot/skills/` and `nanobot/agent/tools/`
- PicoClaw (`./picoclaw/`): Go, check `workspace/skills/` and `pkg/tools/`
- IronClaw (`./ironclaw/`): Rust + WASM, check `src/tools/builtin/` and `tools-src/`
- TinyClaw (`./tinyclaw/`): TS/Bash, check `.agents/skills/` directory

---

### 2. Heartbeat System

**What it does**: A IA acorda a cada 30 minutos para verificar se algo precisa de atenção. Proativa, não apenas reativa.

**Reference implementations**: OpenClaw, PicoClaw, NanoBot, IronClaw, ZeroClaw

**Where to find reference code**:
- OpenClaw (`./openclaw/`): TypeScript, check `skills/` and `extensions/` directories
- ZeroClaw (`./zeroclaw/`): Rust trait-based, check `src/tools/` directory
- NanoBot (`./nanobot/`): Python, check `nanobot/skills/` and `nanobot/agent/tools/`
- PicoClaw (`./picoclaw/`): Go, check `workspace/skills/` and `pkg/tools/`
- IronClaw (`./ironclaw/`): Rust + WASM, check `src/tools/builtin/` and `tools-src/`

---

## Integrações e Protocolos

### 1. OpenRouter 100+ Models

**What it does**: Acesse Claude, GPT-4, Gemini, Mistral, DeepSeek, Llama e mais de 100 modelos com uma única chave de API. Troque de modelo sem mudar o código. Ideal como provider principal com Ollama como fallback local.

**Reference implementations**: OpenRouter, Antidote, NanoBot

**Where to find reference code**:
- NanoBot (`./nanobot/`): Python, check `nanobot/skills/` and `nanobot/agent/tools/`

---

## Implementation Notes for Claude Code

When building this framework, follow these principles:

1. **Start with the reference code** - Each item above lists which repos implement it. Read those implementations first.
2. **Prefer simplicity** - If NanoClaw (5.2K lines) and OpenClaw (large) both implement a feature, start with NanoClaw's approach.
3. **Keep it modular** - Use ZeroClaw/IronClaw's trait-based pattern so components can be swapped later.
4. **Security by default** - Apply sandboxing, command blocklists, and pairing codes from the start.
5. **Full deep-dive reference** - See `FRAMEWORK-DEEP-DIVE.md` for complete architectural analysis of all 9 repos.

---

*Generated from the AI Agent Framework Grocery Store comparison tool.*
