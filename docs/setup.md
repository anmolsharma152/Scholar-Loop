# Scholar-Loop — setup

| Field | Value |
|-------|--------|
| **As of** | 2026-07-19 |
| **Stack** | Python 3.12+ · FSRS · Groq · Resend · GitHub Actions |

Handoff: [STATUS.md](./STATUS.md).

---

## Prerequisites

- Python 3.12+  
- [Resend](https://resend.com) API key  
- [Groq](https://console.groq.com) API key (quiz generation)  
- GitHub repo secrets for Actions (if using cron)

---

## Environment

Copy `.env.example` → `.env` (never commit):

| Variable | Purpose |
|----------|---------|
| `RESEND_API_KEY` | Email delivery |
| `RECIPIENT` / from address vars | Where digests go |
| `GROQ_API_KEY` | Quiz / enhancement LLM |

Load:

```bash
set -a && source .env && set +a
```

---

## Local install

```bash
cd ~/Projects/Scholar-Loop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `python agent/send_daily.py --dry-run --mode learn` | Preview learn picks (no email) |
| `python agent/send_daily.py --dry-run --mode quiz` | Preview quiz |
| `python agent/send_daily.py --mode learn` | Send learn |
| `python agent/send_daily.py --mode quiz` | Send quiz |
| `python agent/send_daily.py --mode both` | Both modes |
| `python scripts/convert_notes.py <file>` | Ingest PDF/DOCX → knowledge |

---

## Production cron

GitHub Actions workflow (dual schedule → learn / quiz).  
DB commit uses `[skip ci]` to avoid loops.  
Secrets: set Resend + Groq in repository secrets.

---

## Note format

Scheduling state lives in **`data/user.db`**, not frontmatter. Frontmatter holds topic metadata and optional `sequence` for curriculum.

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
- Treat `data/user.db` as state (Actions may rewrite on main)  
- Keep `knowledge/archive/` and `knowledge/obsidian/` excluded from agent selection
