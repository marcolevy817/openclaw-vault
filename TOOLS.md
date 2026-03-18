# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Gemini API

- **API Key:** `AIzaSyCGMrw7_ezmTTKHbz7CzFKzhZbZQhLF-Dw`
- **Image generation models:** `imagen-4.0-generate-001` (paid), `gemini-2.5-flash-image` (paid tier)
- **Free tier text models:** `gemini-2.0-flash`, `gemini-2.5-flash`
- **Note:** Image generation requires billing enabled at https://ai.dev/projects
- **Script:** `.tmp/gen_images.py` — generates images via Imagen 4 / Gemini Flash Image

## AgentMail

- **API Key:** `am_us_c133aa641b105571796bc70d60642d230c1da178301ab02d747d415bfea61266`
- **Primary inbox:** `marco-assistant@agentmail.to`
- **API base:** `https://api.agentmail.to/v0`
- Send: `POST /inboxes/{inbox_id}/messages/send`

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
