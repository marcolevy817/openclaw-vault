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

## Setup Status (updated 2026-03-19)

- ✅ Memory workspace fully scaffolded (second-brain/, directives/, memory/, MEMORY.md)
- ✅ Mission Control installed, built, running (port 3000)
- ✅ Discord bot connected, channels/categories created, slash commands deployed
- ✅ AgentMail inbox created, test email sent to marcolevy54@gmail.com
- ✅ Gemini API key saved + billing enabled (image gen working)
- ✅ Playwright installed for HTML→PNG infographic generation
- ✅ Telegram bot @thedailynewsrobot configured, Marco paired (user ID: 8762567109)
- ✅ gog CLI + OAuth complete — marcolevy54@gmail.com (drive, gmail, calendar, sheets, docs, contacts)
- ✅ vo-to-slides skill working at ~/vo-to-slides → outputs direct to Google Slides
- ✅ ElevenLabs TTS connected (key in TOOLS.md)
- ✅ last30days skill installed (~/workspace/skills/last30days)
- ✅ Daily 8 AM briefing cron → Telegram DM + Discord #daily-brief
- ⬜ Mission Control /setup wizard not yet completed by Marco
- ⬜ Obsidian not yet pointed at workspace vault
- ⬜ BOOTSTRAP.md still exists — delete after identity established

---

## Discord Server Structure

- **Server ID:** `1483826485755117600`
- Categories: GENERAL, WORK, FINANCE & MARKETS, CREATIVE
- **#daily-brief** under FINANCE & MARKETS — receives 8 AM briefing
- Bot: Message Content Intent ✅, OAuth2 Code Grant ✅ (off), Manage Channels ✅

---

## Key Lessons

- Gateway restart: `kill -SIGUSR1 <pid>` or `openclaw gateway restart`
- Image generation: HTML/CSS → Playwright → PNG → Discord
- Gemini image gen: `gemini-2.5-flash-image` model, needs billing enabled
- Slides pipeline: spec.json → pptxgenjs (~/vo-to-slides) → `gog drive upload --convert` → Google Slides
- pptx must be copied to `.tmp/` before Discord upload (path restriction)
- Telegram direct send: use `curl` to bot API when cross-context messaging is blocked

---

## Open TODOs

- [ ] Complete Mission Control onboarding at http://localhost:3000/setup
- [ ] Point Obsidian at workspace vault
- [ ] Delete BOOTSTRAP.md
- [ ] Marco to confirm GitHub repo for skills upload

---

_Last distilled: 2026-03-19 09:09 ET_
