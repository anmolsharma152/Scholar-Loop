# Scholar-Loop

> Personal spaced-repetition agent that emails you FSRS-scheduled Learn + Quiz every day across DSA, System Design, ML-AI, and more.

Built on FSRS spacing, Groq-generated quizzes, proportional topic allocation, and GitHub Actions for zero-maintenance delivery.

---

## How it works

```
┌──────────────────────────────────────────────┐
│  knowledge/          223 notes across        │
│  ├── dsa/             7 topics, YAML        │
│  ├── system-design/   frontmatter with      │
│  ├── ml-ai/           topic · difficulty    │
│  ├── fullstack/       tags · last_sent      │
│  ├── papers/          review_count          │
│  ├── agentic-ai/                            │
│  └── sql/                                   │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│  data/user.db    SQLite with FSRS state      │
│  notes table:    path · stability ·          │
│                  difficulty_fsrs · due ·     │
│                  review_count · last_sent    │
│  reviews table:  note_id · sent_at · grade   │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│  agent/send_daily.py                         │
│                                              │
│  🧠 LEARN (morning)                          │
│  1. Proportional topic selection             │
│     DSA 35% · System Design 20% · ...        │
│  2. Pick due notes (lowest retrievability)   │
│  3. Render raw .md content as HTML            │
│  4. Send immediately via Resend              │
│                                              │
│  📝 QUIZ (evening)                           │
│  1. Pick previously-sent notes               │
│  2. Groq generates 3 Q&A per note            │
│  3. Answers hidden in <details> spoiler      │
│  4. Send scheduled via Resend (4PM IST)      │
│                                              │
│  Both outcomes committed to user.db          │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│  .github/workflows/daily-email.yml           │
│  Cron: 03:13 UTC (08:43 IST) — off-peak      │
│  Single run → learn (immediate) + quiz (4PM) │
│  Trigger: also supports workflow_dispatch    │
└──────────────────────────────────────────────┘
```

---

## Knowledge base

| Topic | Notes | Content |
|-------|-------|---------|
| `dsa/` | 41 | Data structures, algorithms, complexity |
| `papers/` | 70 | AI research paper summaries (Transformer → DeepSeek-R1) |
| `ml-ai/` | 60 | ML fundamentals, deep learning, RL, CV, NLP, vision transformers |
| `fullstack/` | 22 | Python, FastAPI, TypeScript, React |
| `system-design/` | 13 | Distributed systems, DDIA, ML system design |
| `sql/` | 9 | SQL fundamentals through window functions |
| `agentic-ai/` | 8 | RAG, multi-agent systems, prompt engineering |

---

## Getting started

### Prerequisites

- Python 3.12+
- [Resend](https://resend.com) API key — email delivery
- [Groq](https://console.groq.com) API key — quiz generation (optional but recommended)

### Local setup

```bash
git clone https://github.com/anmolsharma152/Scholar-Loop
cd Scholar-Loop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
source .env
```

### Dry-run (no email sent)

```bash
source .env
python agent/send_daily.py --dry-run
# prints selected notes, topics, and quiz candidates
```

### Run learn only

```bash
source .env
python agent/send_daily.py --dry-run --mode learn
```

### Run quiz only

```bash
source .env
python agent/send_daily.py --dry-run --mode quiz
```

### Send a real email

```bash
source .env
python agent/send_daily.py
# sends Learn immediately + Quiz scheduled for 4PM IST
```

---

## Note format

Every note needs YAML frontmatter. The agent reads `topic`, `difficulty`, `last_sent`, and `review_count` to schedule notes.

```yaml
---
topic: dsa                # dsa | system-design | ml-ai | fullstack | papers | agentic-ai | sql
difficulty: medium        # easy | medium | hard
tags: [arrays, sliding-window]
last_sent:                # set automatically after each send
review_count: 0           # incremented automatically after each send
---

# Your Note Title

Content here — markdown with code blocks, tables, and LaTeX all supported.
```

---

## Selection & scheduling

### Topic weights

| Topic | Weight | Effective per email |
|-------|--------|-------------------|
| DSA | 35% | ~2-3 notes |
| System Design | 20% | ~1 note |
| SQL | 10% | ~1 note (shared slot) |
| Fullstack | 10% | |
| ML-AI | 10% | |
| Papers | 8% | |
| Agentic AI | 7% | |

Notes are picked by lowest FSRS retrievability within each topic's allocation.

### Learn vs Quiz

| | Learn (morning) | Quiz (evening) |
|---|---|---|
| **Content** | Full note rendered as HTML | 3 Q&A per note, hidden behind spoiler |
| **Selection** | Due notes, proportional by topic | Previously-sent notes |
| **Delivery** | Immediate | Scheduled for 4PM IST via Resend |
| **Groq** | Not used (raw note content) | Generates questions from note text |

---

## Deployment

### GitHub Actions (automated)

The cron fires at **03:13 UTC (08:43 IST)** — an off-peak minute to avoid runner congestion. A single run sends both Learn (immediate) and Quiz (scheduled for 4PM IST).

Add these secrets to **Settings → Secrets and variables → Actions**:

| Secret | Required | Value |
|--------|----------|-------|
| `RESEND_API_KEY` | ✅ | From [resend.com/api-keys](https://resend.com/api-keys) |
| `RECIPIENT` | ✅ | Your email address |
| `GROQ_API_KEY` | Recommended | From [console.groq.com](https://console.groq.com) |

After each send, the workflow commits updated `data/user.db` with `[skip ci]`.

### Manual trigger

Go to **Actions → daily-email → Run workflow** to send immediately without waiting for the cron.

---

## Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `RESEND_API_KEY` | Yes | — | Email delivery |
| `RECIPIENT` | Yes | — | Destination email address |
| `GROQ_API_KEY` | No | — | Enables quiz generation |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Override Groq model |

---

## Roadmap

| Version | Status | Description |
|---------|--------|-------------|
| **MVP** | ✅ | Weighted-random picker, Groq enhancement, Resend delivery |
| **V1** | ✅ | FSRS scheduling, proportional topic allocation, Learn/Quiz split |
| **V1.5** | Planned | Grade feedback loop (capture quiz responses → update FSRS params) |
| **V2** | Planned | Multi-user with Google OAuth, per-user FSRS state |
| **V2.5** | Planned | Live watchers — `arxiv_watch.py`, `feed_watch.py` |
