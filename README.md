# Scholar-Loop

> Personal spaced-repetition agent that emails you FSRS-scheduled **Learn** (morning) and **Quiz** (evening) digests — DSA, System Design, ML/AI, papers, and more.

**Engineered by [Anmol Sharma](https://linkedin.com/in/anmolsharma152)** | **[GitHub Profile](https://github.com/anmolsharma152)** | **[Live Portfolio](https://anmolsharma152.vercel.app)**

Built on [FSRS](https://github.com/open-spaced-repetition/fsrs4anki) scheduling, proportional topic allocation, optional DSA curriculum order, Groq quizzes, Resend delivery, and GitHub Actions.

**Portfolio:** Scholar-Loop owns *retain knowledge on a schedule* only. Not ops (Ozyman), not job boards (Disha), not creative synthesis (IdeaForge). See [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md).

## Docs (start here)

| Doc | Purpose |
|-----|---------|
| **[docs/STATUS.md](./docs/STATUS.md)** | Handoff — what works, gaps, resume |
| [docs/setup.md](./docs/setup.md) | Env, dry-run, cron |
| [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md) | Scholar-Loop vs siblings |
| [AGENTS.md](./AGENTS.md) | Guidance for coding agents |

---

## How it works

```
┌──────────────────────────────────────────────┐
│  knowledge/          223 notes · 7 topics    │
│  ├── dsa/            YAML: topic, difficulty │
│  ├── system-design/  optional: tags, sequence│
│  ├── ml-ai/                                  │
│  ├── fullstack/ · papers/ · sql/ · agentic-ai│
└──────────────────┬───────────────────────────┘
                   │  scripts/init_db.py
┌──────────────────▼───────────────────────────┐
│  data/user.db    SQLite FSRS state           │
│  notes: stability · difficulty_fsrs · due    │
│         state · step · last_sent · sequence  │
│  reviews: note_id · sent_at · grade          │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│  agent/send_daily.py                         │
│                                              │
│  LEARN (morning)                             │
│  · Proportional topic slots (DSA 35%, …)     │
│  · Due notes first (NULLS LAST); sequence gate│
│  · Dynamic word cap (~1500w) for 2–3 notes   │
│  · Markdown → HTML → Resend (immediate)      │
│  · Passive FSRS Good → multi-day next due     │
│                                              │
│  QUIZ (evening)                              │
│  · Partition-diverse previously-sent notes   │
│  · Groq: 3 Q&As (Q1–Q3) + answers (A1–A3)    │
│  · Newsletter bottom solution block          │
│  · Resend immediate (separate cron)          │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│  GitHub Actions dual cron                    │
│  01:47 UTC (07:17 IST) → --mode learn        │
│  09:47 UTC (15:17 IST) → --mode quiz         │
│  Commits data/user.db with [skip ci]         │
└──────────────────────────────────────────────┘
```

---

## Knowledge base

| Topic | Notes | Role |
|-------|------:|------|
| `dsa/` | 41 | Algorithms + math foundations; **`sequence` curriculum** |
| `papers/` | 70 | Paper summaries (Transformer → DeepSeek-R1, …) |
| `ml-ai/` | 60 | DL, RL, CV, NLP, transformers |
| `fullstack/` | 22 | Python, FastAPI, TypeScript, React, data tools |
| `system-design/` | 13 | Distributed systems, DDIA, ML system design |
| `sql/` | 9 | Basics through windows / interview patterns |
| `agentic-ai/` | 8 | RAG, multi-agent, prompts |

Excluded from the agent: `knowledge/archive/`, `knowledge/obsidian/`.

---

## Getting started

### Prerequisites

- Python 3.12+
- [Resend](https://resend.com) API key — email delivery
- [Groq](https://console.groq.com) API key — quiz generation (recommended)

### Local setup

```bash
git clone https://github.com/anmolsharma152/Scholar-Loop
cd Scholar-Loop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in RESEND_API_KEY, RECIPIENT, GROQ_API_KEY
set -a && source .env && set +a
python scripts/init_db.py   # knowledge/ → data/user.db
```

### Dry-run (no email)

```bash
python agent/send_daily.py --dry-run --mode learn
# prints topic slots + each pick: path, due, stability (S), review_count, sequence
python agent/send_daily.py --dry-run --mode quiz
```

### Send for real

```bash
python agent/send_daily.py --mode learn
python agent/send_daily.py --mode quiz
# or both modes in one process:
python agent/send_daily.py --mode both
```

### Ingest PDFs / Obsidian Notes

```bash
# Convert research PDFs/DOCX into study notes:
python scripts/convert_notes.py ~/Downloads/some-paper.pdf

# Ingest and chunk large Obsidian guides into atomic notes:
python scripts/ingest_obsidian.py knowledge/obsidian/some-guide.md ml-ai
```

---

## Note format

Scheduling state lives in **`data/user.db`**, not frontmatter. Frontmatter is for topic metadata and optional curriculum order.

```yaml
---
topic: dsa                # dsa | system-design | ml-ai | fullstack | papers | agentic-ai | sql
difficulty: medium        # easy | medium | hard
tags: [arrays, sliding-window]
sequence: 4               # optional; DSA uses this for syllabus order
---

# Your Note Title

Markdown with code blocks, tables, and LaTeX-friendly text.
```

---

## Selection & scheduling

### Topic weights (Learn)

| Topic | Weight | Typical share |
|-------|-------:|---------------|
| DSA | 35% | ~1–2 notes |
| System Design | 20% | ~1 |
| SQL | 10% | shared |
| Fullstack | 10% | |
| ML-AI | 10% | |
| Papers | 8% | |
| Agentic AI | 7% | |

Cap: Dynamic length limit (~1500 words, minimum 2 notes) to keep daily reading focused without overwhelming walls of text.

**Learn rules**

1. Allocate slots by weight among topics that have due notes.
2. **Prioritize reviews:** Due reviews are selected first (`due ASC NULLS LAST`), filling the remaining word budget with new curriculum notes.
3. **Sequence gate:** For topics with `sequence` on unsent notes (DSA), only the **minimum unsent sequence** can be introduced. Higher sequences stay locked until earlier ones are sent.
4. After send: Passive FSRS `Rating.Good` with empty learning steps → multi-day `due` (not “due again today”). Grade is logged to `reviews`.

**Quiz rules**

- Selects from notes with `last_sent` set, partitioned by topic for guaranteed multi-topic diversity (`ROW_NUMBER() OVER PARTITION`).
- Groq generates 3 Q&As (`Q1`, `Q2`, `Q3`); answers (`A1:`, `A2:`, `A3:`) are cleanly segregated at the bottom of the email in a newsletter solution block for true active recall.
- Does **not** update FSRS.

### Learn vs Quiz

| | Learn | Quiz |
|---|---|---|
| **When** | 01:47 UTC (07:17 IST → arrives ~07:45–08:00 AM) | 09:47 UTC (15:17 IST → arrives ~03:45–04:00 PM) |
| **Content** | Full note HTML (capped ~1500w) | 3 Q&A (`Q1–Q3`) + bottom answers (`A1–A3`) |
| **Selection** | Due reviews first (`NULLS LAST`) + weights + sequence | Cumulative seen notes with topic diversity |
| **FSRS** | Passive Good | No update |
| **LLM** | No | Groq (`groq/compound-mini`) |

---

## Deployment

### GitHub Actions

Workflow: [`.github/workflows/daily-email.yml`](.github/workflows/daily-email.yml)

| Cron (UTC) | IST (Scheduled) | Expected Delivery | Command |
|------------|-----------------|-------------------|---------|
| `47 1 * * *` | 07:17 | ~07:45–08:00 AM | `python agent/send_daily.py --mode learn` |
| `47 9 * * *` | 15:17 | ~03:45–04:00 PM | `python agent/send_daily.py --mode quiz` |

**Secrets** (Settings → Secrets and variables → Actions):

| Secret | Required | Source |
|--------|----------|--------|
| `RESEND_API_KEY` | Yes | [resend.com/api-keys](https://resend.com/api-keys) |
| `RECIPIENT` | Yes | Your inbox |
| `GROQ_API_KEY` | Recommended | [console.groq.com](https://console.groq.com) |

After each successful run the bot commits `data/user.db` with message `chore: update review metadata [skip ci]`.

Manual run: **Actions → daily-email → Run workflow** (supports choosing `learn` or `quiz` mode).

---

## Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `RESEND_API_KEY` | Yes | — | Email delivery |
| `RECIPIENT` | Yes | — | Destination address |
| `GROQ_API_KEY` | No | — | Quiz (+ convert_notes / ingest) |
| `LLM_MODEL` | No | `groq/compound-mini` | Groq model id |

---

## Development

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
# skip LLM-backed tests if any are marked slow:
python -m pytest tests/ -q -m "not slow"
```

| Path | Role |
|------|------|
| `agent/send_daily.py` | Learn/Quiz selection, FSRS, email rendering |
| `scripts/init_db.py` | Schema + migrate notes into SQLite |
| `scripts/convert_notes.py` | PDF/DOCX → study notes via Groq |
| `scripts/ingest_obsidian.py` | Chunk large Obsidian guides into study notes via Groq |
| `tests/` | Unit tests (slots, FSRS, learn/quiz, convert) |
| `pyproject.toml` | pytest / ruff / coverage config |

---

## Roadmap

| Version | Status | Description |
|---------|--------|-------------|
| **MVP** | ✅ | Weighted pick, email delivery |
| **V1** | ✅ | SQLite FSRS, topic weights, Learn/Quiz split, dual cron |
| **V1.1** | ✅ | Real passive FSRS (fsrs 6.x), DSA sequence, dry-run logging, tests |
| **V1.5** | Partial | Passive grades in `reviews`; interactive Again/Hard/Good still planned |
| **V2** | Planned | Multi-user, OAuth, per-user FSRS |
| **V2.5** | Planned | Live watchers (`arxiv`, feeds) |
