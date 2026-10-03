# Scholar-Loop — setup

| Field | Value |
|-------|--------|
| **As of** | 2026-10-03 |
| **Stack** | Python 3.12 · FSRS · Gemini Flash · Resend · GitHub Actions |

Current state: [../PROJECT_STATE.md](../PROJECT_STATE.md).

---

## Prerequisites

- Python 3.12 (pinned in `.python-version`)
- [Resend](https://resend.com) API key
- [Gemini](https://aistudio.google.com/app/apikey) API key (quiz generation and note ingestion)
- GitHub repo secrets for Actions

---

## Environment

Copy `.env.example` → `.env` (never commit):

| Variable | Purpose |
|----------|---------|
| `RESEND_API_KEY` | Email delivery |
| `RECIPIENT` | Where the digest goes |
| `GEMINI_API_KEY` | Quiz, `convert_notes.py`, `ingest_obsidian.py` |
| `LLM_MODEL` | Optional override (default `gemini-flash-latest`) |

Load:

```bash
set -a && source .env && set +a
```

---

## Local install

```bash
cd ~/Projects/Scholar-Loop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/init_db.py
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `python agent/send_daily.py --dry-run` | Show the day's Learn + Quiz picks (no email, no LLM) |
| `python agent/send_daily.py --preview out.html` | Build the full email with the Gemini quiz; write HTML; no send |
| `python agent/send_daily.py` | Send the combined daily email |
| `python agent/send_daily.py --mode learn` / `--mode quiz` | Send one part alone (debugging) |
| `python scripts/convert_notes.py <file>` | Ingest PDF/DOCX → knowledge |
| `python scripts/ingest_obsidian.py <file> <topic>` | Chunk Obsidian guides into knowledge notes |
| `python -m pytest tests/ -q` | Run tests |

---

## Production cron

- `daily-email.yml`: `47 1 * * 1-5` → 07:17 IST, Monday–Friday, `--mode daily`.
- `tests.yml`: runs pytest on code pushes to `main`.
- The DB commit uses `[skip ci]` to avoid loops.
- Secrets: `RESEND_API_KEY`, `RECIPIENT`, `GEMINI_API_KEY`.

---

## Note format

Scheduling state lives in **`data/user.db`**, not frontmatter. Frontmatter holds topic metadata and an optional `sequence` for curriculum order.

```yaml
---
topic: dsa
difficulty: medium
tags: [arrays]
sequence: 4
---
# Title
```

---

## Hygiene

- Do not commit `.env`
- Treat `data/user.db` as state (Actions rewrites it on `main`)
- Keep `knowledge/archive/` and `knowledge/obsidian/` out of agent selection until ingested
