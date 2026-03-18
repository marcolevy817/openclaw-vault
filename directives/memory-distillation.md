# Directive: Memory Distillation

#directive #memory

## Purpose

Periodically distill raw daily logs into curated long-term memory in `MEMORY.md`.

## When to Run

- During a heartbeat, every few days
- After a significant project or decision

## Steps

1. Read `memory/` files from the last 3–7 days
2. Identify:
   - Key decisions made
   - Important context about Marco or ongoing projects
   - Lessons learned / things that went wrong
   - Open questions or TODOs
3. Update `MEMORY.md`:
   - Add new high-signal entries
   - Remove outdated or superseded entries
   - Keep it short — no raw logs, just distilled insights
4. Update `_Last distilled:` date in `MEMORY.md`
5. Update `memory/heartbeat-state.json` → `lastChecks.memoryDistillation`

## Rules

- MEMORY.md is curated — don't dump everything in
- If an entry is no longer relevant, remove it
- Prefer short bullets over paragraphs
