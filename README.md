# Scholar-Loop

A spaced-repetition learning agent that emails daily study content across DSA,
System Design, ML/AI, Full-stack, and AI research papers. Uses weighted-random
note selection, optional LLM-enhanced recaps and quizzes, and Resend for delivery.

## Architecture

```
  ┌──────────────────────┐
  │   knowledge/         │  Markdown notes with YAML frontmatter
  │   ├── dsa/           │  (topic, difficulty, tags,
  │   ├── system-design/ │   last_sent, review_count)
  │   ├── ml-ai/         │
  │   ├── fullstack/     │
  │   └── papers/        │
  └───────┬──────────────┘
          │
  ┌───────▼──────────────┐
  │  agent/send_daily.py │  Weighted-random picker
  │                      │  score = days_since_sent * 10
  │  ┌──────────────┐    │          - review_count * 5
  │  │ Weighted pick│    │  unsent = priority 1000
  │  │(2 notes/day) │    │
  │  └──────┬───────┘    │
  │         │            │
  │  ┌──────▼───────┐    │
  │  │ Groq LLM     │    │  Optional: recap + quiz
  │  │(llama-3.3)   │    │
  │  └──────┬───────┘    │
  │         │            │
  │  ┌──────▼───────┐    │
  │  │ Resend API   │    │  Email delivery
  │  └──────────────┘    │
  └───────┬──────────────┘
          │
  ┌───────▼──────────────┐
  │ .github/workflows/   │  GitHub Actions cron
  │  daily-email.yml     │  01:30 UTC (07:00 IST)
  └──────────────────────┘
```

### Topic structure

| Directory | Content | Live watcher? |
|-----------|---------|---------------|
| `dsa/` | Data structures & algorithms | No (fundamentals don't go stale) |
| `system-design/` | System design concepts | Planned (RSS feeds) |
| `ml-ai/` | ML/DL concepts & algorithms | Planned (arXiv API) |
| `fullstack/` | Python + JS ecosystem | Planned (GitHub releases.atom) |
| `papers/` | AI research paper summaries | Planned (arXiv API) |

Papers are kept separate from `ml-ai/` so the two can be scored, scheduled,
and consumed independently.

## Getting started

### Prerequisites

- Python 3.12+
- A [Resend](https://resend.com) API key
- A [Groq](https://console.groq.com) API key (for LLM enhancement)
- A [Gemini](https://aistudio.google.com/apikey) API key (for PDF ingestion)

### Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Seed from PDFs

```bash
export GEMINI_API_KEY="..."
python ingestion/pdf_to_notes.py --skip-existing
```

Uses Gemini 2.5 Flash for native PDF understanding and structured markdown
extraction. Outputs notes with YAML frontmatter ready for the email rotation.

### Dry-run

```bash
export GROQ_API_KEY="..."
python agent/send_daily.py --dry-run
```

Prints selected notes, their scores, and LLM-enhanced output without sending.

### Send a test email

```bash
export RESEND_API_KEY="..."
export RECIPIENT="your@email.com"
export GROQ_API_KEY="..."
python agent/send_daily.py
```

## Note format

Every note must have YAML frontmatter:

```yaml
---
difficulty: easy|medium|hard
last_sent:
review_count: 0
tags:
  - relevant-tag
  - another-tag
topic: dsa|system-design|ml-ai|fullstack|papers
---
```

Code blocks, tables, LaTeX, and images are all supported in the markdown body.

## Scoring algorithm

```python
if never_sent:
    score = 1000
else:
    score = days_since_last_sent * 10 - review_count * 5
    score = max(score, 1)
```

Two notes from different topics are picked per day via weighted random selection.

## LLM enhancement

When `GROQ_API_KEY` is set, Groq (Llama 3.3 70B) adds a recap and quiz:

1. **Quick recap** — 2-3 sentence summary at the top
2. **Quiz** — 3 questions with answers in `<details>` tags

## Delivery

[Resend](https://resend.com) handles email delivery with dashboard and delivery
tracking. The GitHub Actions workflow commits updated `last_sent` and
`review_count` metadata after each send, using `[skip ci]` to prevent infinite
workflow loops.

## Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `RESEND_API_KEY` | Yes | Email delivery via Resend |
| `RECIPIENT` | Yes | Email recipient address |
| `GROQ_API_KEY` | For LLM | Groq API key for recap + quiz |
| `GEMINI_API_KEY` | For PDFs | Gemini API key for PDF ingestion |
| `LLM_MODEL` | No | Override Groq model (default: `llama-3.3-70b-versatile`) |

## Deployment

Add the required secrets to the repo's Settings → Secrets and variables →
Actions. The daily cron (`30 1 * * *` / 07:00 IST) runs automatically.

## Build roadmap

- **MVP** (current): Weighted-random picker, Groq enhancement, Resend delivery
- **V1.5**: Live watchers (`arxiv_watch.py`, `feed_watch.py`) with human-review queue
- **V2**: LangGraph agent with Gemini 2.5 Flash orchestration, RAG over notes
- **V2.5**: SM-2 spaced-repetition schedule replacing weighted-random scoring

## Model routing (V2+)

- **Gemini 2.5 Flash** — Orchestration, tool-calling, PDF ingestion. Native
  PDF understanding and strong function-calling for the LangGraph tool graph.
- **Groq (Llama 3.3 70B)** — Synthesis. Fast recap and quiz generation.
