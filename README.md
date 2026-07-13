# Scholar-Loop

> A personal spaced-repetition agent that emails you 2 study notes every morning — picked by score, enhanced by an LLM, and delivered before you open Slack.

Built on weighted-random scoring, Groq-powered recaps + quizzes, and GitHub Actions for zero-maintenance delivery.

---

## How it works

```
┌─────────────────────────────────────────┐
│  knowledge/          193 notes across   │
│  ├── dsa/            7 topics, YAML     │
│  ├── system-design/  frontmatter with   │
│  ├── ml-ai/          topic · difficulty │
│  ├── fullstack/      tags · last_sent   │
│  ├── papers/         review_count       │
│  ├── agentic-ai/                        │
│  └── sql/                               │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  agent/send_daily.py                    │
│                                         │
│  1. Score every note                    │
│     unsent         → 1000               │
│     sent before    → days×10 − reviews×5│
│                                         │
│  2. Pick 2 from different topics        │
│     (weighted random)                   │
│                                         │
│  3. Enhance with Groq (optional)        │
│     Llama 3.3 70B → recap + quiz        │
│                                         │
│  4. Send via Resend                     │
│                                         │
│  5. Commit updated metadata [skip ci]   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  .github/workflows/daily-email.yml      │
│  Cron: 01:30 UTC  (07:00 IST)           │
│  Trigger: also supports workflow_dispatch│
└─────────────────────────────────────────┘
```

---

## Knowledge base

| Topic | Notes | Content |
|-------|-------|---------|
| `dsa/` | 41 | Data structures, algorithms, complexity |
| `ml-ai/` | 53 | ML fundamentals, deep learning, RL, CV, NLP |
| `papers/` | 64 | AI research paper summaries (Transformer → DeepSeek-R1) |
| `system-design/` | 13 | Distributed systems, DDIA, ML system design |
| `fullstack/` | 13 | Python, FastAPI, TypeScript, React |
| `agentic-ai/` | 5 | RAG, multi-agent systems, LLM serving, prompt engineering |
| `sql/` | 4 | SQL fundamentals through window functions |

Papers are kept separate from `ml-ai/` so they can be scored and scheduled independently.

---

## Getting started

### Prerequisites

- Python 3.12+
- [Resend](https://resend.com) API key — email delivery
- [Groq](https://console.groq.com) API key — LLM recap + quiz (optional but recommended)

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
# prints selected notes, paths, and scores
```

### Force a specific topic

```bash
python agent/send_daily.py --dry-run --topic papers
python agent/send_daily.py --dry-run --topic dsa
```

### Send a real email

```bash
source .env
python agent/send_daily.py
```

---

## Note format

Every note needs YAML frontmatter. The agent reads `topic`, `difficulty`, `last_sent`, and `review_count` to score and pick notes.

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

The email title is extracted from the first `# H1` heading in the note body — not the filename.

---

## Scoring

```python
if never_sent:
    score = 1000              # unsent notes have highest priority
else:
    score = days_since_last_sent * 10 - review_count * 5
    score = max(score, 1)     # floor at 1 so nothing is permanently excluded
```

Two notes from **different topics** are picked per day via weighted-random selection. Notes you've seen recently and frequently are naturally deprioritised.

---

## LLM enhancement

When `GROQ_API_KEY` is set, Groq (Llama 3.3 70B Versatile) wraps each note with:

1. **Quick recap** — 2–3 sentence summary of the core idea
2. **Quiz** — 3 questions with answers hidden in `<details>` tags

Falls back gracefully to raw note content if the key is missing or the API errors.

---

## Deployment

### GitHub Actions (automated)

The cron fires at **01:30 UTC (07:00 IST)** every day. It also supports `workflow_dispatch` for manual triggers.

Add these secrets to **Settings → Secrets and variables → Actions**:

| Secret | Required | Value |
|--------|----------|-------|
| `RESEND_API_KEY` | ✅ | From [resend.com/api-keys](https://resend.com/api-keys) |
| `RECIPIENT` | ✅ | Your email address |
| `GROQ_API_KEY` | Recommended | From [console.groq.com](https://console.groq.com) |

After each send, the workflow commits updated `last_sent` / `review_count` metadata back to the repo with `[skip ci]` to prevent loop triggers.

### Manual trigger

Go to **Actions → daily-email → Run workflow** to send immediately without waiting for the cron.

---

## Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `RESEND_API_KEY` | Yes | — | Email delivery |
| `RECIPIENT` | Yes | — | Destination email address |
| `GROQ_API_KEY` | No | — | Enables LLM recap + quiz |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` | Override Groq model |

---

## Roadmap

| Version | Status | Description |
|---------|--------|-------------|
| **MVP** | ✅ Done | Weighted-random picker, Groq enhancement, Resend delivery |
| **V1.5** | Planned | Live watchers — `arxiv_watch.py`, `feed_watch.py` with human-review queue |
| **V2** | Planned | LangGraph agent with Gemini 2.5 Flash orchestration + RAG over notes |
| **V2.5** | Planned | SM-2 spaced-repetition replacing weighted-random scoring |

### Model routing (V2+)

- **Gemini 2.5 Flash** — orchestration, tool-calling, RAG
- **Groq Llama 3.3 70B** — fast synthesis, recap + quiz generation
