# Concept: OpenClaw Memory System

#concept #memory #openclaw

## Core Idea

The AI doesn't *have* memory — it *reads* memory. OpenClaw injects workspace files into the system prompt at session start, giving the AI persistent context across sessions.

## Three Components

1. **OpenClaw** — reads workspace files at startup, injects them into the system prompt
2. **Obsidian** — vault pointed at the workspace; Graph View shows connections between files
3. **QMD** (optional) — on-device semantic search for finding relevant context without loading everything

## How It Works

- Files in the workspace root are always available to the AI
- Updating a file = updating what the AI knows next session
- Write important things to files — don't just say them in chat

## Key Files

| File | Role |
|---|---|
| `MEMORY.md` | Long-term curated memory |
| `memory/YYYY-MM-DD.md` | Raw daily session logs |
| `second-brain/` | Structured knowledge base |
| `HEARTBEAT.md` | Drives proactive AI behavior |
| `SOUL.md` | AI persona |
| `USER.md` | Human context |

## Links

- [[MEMORY]]
- [[../../second-brain/README]]
