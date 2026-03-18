# MEMORY.md — Long-Term Memory

> Curated insights distilled from daily session logs. Keep this short and high-signal.
> Updated periodically (not every session). Only loaded in the main session.

---

## About Marco

- **Name:** Marco (marco.levy on Discord)
- **Timezone:** America/New_York (Atlanta, ET)
- **Discord user ID:** `689254984638136523`
- **First setup:** 2026-03-18

---

## Infrastructure (as of 2026-03-18)

- **Workspace:** `/Users/xcm-mac/.openclaw/workspace` — Obsidian vault root
- **Mission Control:** `~/mission-control` → http://localhost:3000 — connected to OpenClaw gateway
- **AgentMail inbox:** `marco-assistant@agentmail.to` — API key in TOOLS.md
- **Gemini API key:** in TOOLS.md — free tier, image generation requires billing enabled at ai.dev/projects
- **Discord server ID:** `1483826485755117600`
- **Gateway token:** `d341c4201625a051c8fef7ba695975ed20e03d573869efc1`

---

## Setup Status (2026-03-18)

- ✅ Memory workspace fully scaffolded (second-brain/, directives/, memory/, MEMORY.md)
- ✅ Mission Control installed, built, running (port 3000)
- ✅ Discord bot connected, channels/categories created, slash commands deployed
- ✅ AgentMail inbox created, test email sent to marcolevy54@gmail.com
- ✅ Gemini API key saved — needs billing enabled for image generation
- ✅ Playwright installed for HTML→PNG infographic generation
- ⬜ Mission Control /setup wizard not yet completed by Marco
- ⬜ Obsidian not yet pointed at workspace vault
- ⬜ BOOTSTRAP.md still exists — delete after identity established
- ⬜ GitHub repo for skills not yet confirmed by Marco
- ⬜ Gemini billing not yet enabled (blocks image gen)

---

## Discord Server Structure

- **Server ID:** `1483826485755117600`
- Categories: GENERAL, WORK, FINANCE & MARKETS, CREATIVE
- Bot: Message Content Intent ✅, OAuth2 Code Grant ✅ (off), Manage Channels ✅

---

## Key Lessons

- Gateway restart: `kill -SIGUSR1 <pid>` or `openclaw gateway restart`
- Image generation pipeline: HTML/CSS → Playwright headless Chromium → PNG → Discord
- Gemini image models need paid tier; free tier quota is 0 for image generation

---

## Open TODOs

- [ ] Marco to enable Gemini billing → then re-run `.tmp/gen_images.py`
- [ ] Marco to confirm GitHub repo for skills upload
- [ ] Complete Mission Control onboarding at http://localhost:3000/setup
- [ ] Point Obsidian at workspace vault
- [ ] Delete BOOTSTRAP.md

---

_Last distilled: 2026-03-18 12:07 ET_
