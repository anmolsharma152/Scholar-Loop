# Scholar-Loop — status handoff

| Field | Value |
|-------|--------|
| **As of** | 2026-07-19 |
| **Branch** | `main` |
| **Product** | FSRS-scheduled Learn (morning) + Quiz (evening) digests over personal knowledge |
| **Not this product** | Ozyman (ops) · Disha (jobs) · IdeaForge (creative synthesis) |

Older narrative handoff: [scholar_loop_handoff.md](./scholar_loop_handoff.md).  
Portfolio: [portfolio-product-boundaries.md](./portfolio-product-boundaries.md).  
Setup: [setup.md](./setup.md). Agents: [../AGENTS.md](../AGENTS.md).

---

## What ships today

| Surface | Status | Notes |
|---------|--------|-------|
| Knowledge base | ✅ | Multi-topic markdown under `knowledge/` (DSA sequence curriculum, papers, ML, …) |
| FSRS state | ✅ | SQLite `data/user.db` (stability, due, reviews) |
| Learn mode | ✅ | Proportional topic slots; sequence gate for DSA |
| Quiz mode | ✅ | Groq 3 Q&A + highlight-to-reveal answers |
| Email delivery | ✅ | Resend immediate send |
| GitHub Actions dual cron | ✅ | Learn + Quiz UTC schedules; commits DB with `[skip ci]` |
| PDF/DOCX ingest helpers | ✅ | `scripts/convert_notes.py` |

---

## Architecture snapshot

```text
knowledge/*.md  →  scripts/init_db.py  →  data/user.db (FSRS)
                         ↓
              agent/send_daily.py  --mode learn|quiz|both
                         ↓
              Resend email  +  optional git commit of DB (Actions)
```

---

## Known gaps / next

### P1
- [ ] arXiv / source watchers for new paper queue (planned Phase 1.5)  
- [ ] LangGraph refactor of send_daily (planned; not required for production digests)  
- [ ] Stronger active recall grading (user replies → FSRS grade) vs passive Good

### P2
- [ ] Optional Scholar↔IdeaForge “idea review” export (deep link only)  
- [ ] UI shell (not required for email MVP)

### Explicit non-goals
- Job scoring → **Disha**  
- Operator mail/GitHub → **Ozyman**  
- Creative synthesis engine → **IdeaForge**

---

## Local dev checklist

```bash
cd ~/Projects/Scholar-Loop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # RESEND_*, RECIPIENT, GROQ_API_KEY
set -a && source .env && set +a
python scripts/init_db.py
python agent/send_daily.py --dry-run --mode learn
python agent/send_daily.py --dry-run --mode quiz
```

---

## Resume protocol

1. Read this file + portfolio boundaries.  
2. Prefer dry-run before live Resend.  
3. Don’t rewrite FSRS state casually; back up `data/user.db` if experimenting.  
4. Atomic commits; secrets only in GH Actions secrets / local `.env`.
