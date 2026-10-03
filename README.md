# Scholar-Loop

> Personal spaced-repetition agent that emails one FSRS-scheduled **Learn + Quiz** digest every weekday morning, covering DSA, System Design, ML/AI, Fullstack, and research papers.

**Engineered by [Anmol Sharma](https://linkedin.com/in/anmolsharma152)** | **[GitHub Profile](https://github.com/anmolsharma152)** | **[Live Portfolio](https://anmolsharma152.vercel.app)**

Built on [FSRS](https://github.com/open-spaced-repetition/fsrs4anki) scheduling, proportional topic allocation, DSA curriculum order, Gemini-generated quizzes, Resend delivery, and GitHub Actions.

**Portfolio:** Scholar-Loop owns *retain knowledge on a schedule* only. Not ops (Ozyman), not job boards (Disha), not creative synthesis (IdeaForge). See [docs/portfolio-product-boundaries.md](./docs/portfolio-product-boundaries.md).

## Docs (start here)

| Doc | Purpose |
|-----|---------|
| **[PROJECT_STATE.md](./PROJECT_STATE.md)** | Current state, constraints, next tasks |
| [SESSION_HANDOFF.md](./SESSION_HANDOFF.md) | Latest session notes for resuming work |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design and trade-offs |
| [TASKS.md](./TASKS.md) | Roadmap and task list |
| [docs/setup.md](./docs/setup.md) | Env, commands, deployment |
| [AGENTS.md](./AGENTS.md) | Guidance for coding agents |

---

## How it works

```
knowledge/*.md ──► scripts/init_db.py ──► data/user.db (FSRS state)
                                               │
                         agent/send_daily.py --mode daily
                                               │
        ┌──────────────────────────────────────┴───────────────────────┐
        │ Part 1 · Learn   2–3 due notes (~1500 words), FSRS updated    │
        │ Part 2 · Quiz    1–2 earlier notes, 3–6 questions (Gemini)    │
        │ Answers          at the bottom, below a divider               │
        └──────────────────────────────────────┬───────────────────────┘
                                               │
                         Resend ──► your inbox (Mon–Fri ~07:45 IST)
                                               │
              GitHub Actions commits data/user.db with [skip ci]
```

---

## The daily email

One email, Monday to Friday. Nothing on weekends.

1. **Part 1 · Today's notes.** Full note content: code, tables, and explanations. Due reviews come first, then new notes; DSA follows its `sequence` order. Capped at about 1,500 words with at least 2 notes. Each note gets a passive FSRS `Good` review, which schedules its next due date.
2. **Part 2 · Active recall.** 3 questions each for 1–2 notes you studied earlier. Today's Learn notes are never quizzed. Picks rotate: least recently quizzed first, then weakest memory (lowest FSRS stability). The quiz does **not** change FSRS scheduling.
3. **Answers.** At the bottom, below a dashed divider, so you can test yourself before scrolling.

Subject: `📚 Scholar-Loop: System Design and DSA — Learn & Quiz`

**If Gemini fails**, the email still goes out with the Learn notes and a "Quiz unavailable today" notice, and the GitHub run shows a warning. An LLM outage never blocks your notes, and it can't fail silently either.

---

## Knowledge base

| Topic | Notes | Weight | Role |
|-------|------:|-------:|------|
| `dsa/` | 41 | 28% | Algorithms + math foundations; **`sequence` curriculum** |
| `ml-ai/` | 60 | 22% | DL, RL, CV, NLP, transformers |
| `papers/` | 70 | 20% | Paper summaries (Transformer → DeepSeek-R1, …) |
| `system-design/` | 21 | 16% | Distributed systems, agentic AI, ML system design |
| `fullstack/` | 31 | 14% | Python, FastAPI, TypeScript, React, SQL |

Not in rotation: `knowledge/archive/` (retired notes) and `knowledge/obsidian/` (raw guides waiting to be ingested).

---

## Getting started

### Prerequisites

- Python 3.12+
- [Resend](https://resend.com) API key for email delivery
- [Gemini](https://aistudio.google.com/app/apikey) API key for quiz generation

### Local setup

```bash
git clone https://github.com/anmolsharma152/Scholar-Loop
cd Scholar-Loop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # fill in RESEND_API_KEY, RECIPIENT, GEMINI_API_KEY
set -a && source .env && set +a
python scripts/init_db.py   # knowledge/ → data/user.db
```

### Preview without sending

```bash
python agent/send_daily.py --dry-run
# prints the Learn and Quiz picks: path, due, stability (S), review_count, sequence

python agent/send_daily.py --preview /tmp/scholar.html
# builds the full email including the Gemini quiz, writes the HTML, prints its size.
# Sends nothing and leaves scheduling data unchanged.
```

### Send for real

```bash
python agent/send_daily.py              # combined daily email (default)
python agent/send_daily.py --mode learn # Learn notes only
python agent/send_daily.py --mode quiz  # Quiz only
```

### Ingest PDFs / Obsidian notes

```bash
python scripts/convert_notes.py ~/Downloads/some-paper.pdf
python scripts/ingest_obsidian.py knowledge/obsidian/some-guide.md ml-ai
```

---

## Note format

Scheduling state lives in **`data/user.db`**, not frontmatter.

```yaml
---
topic: dsa                # dsa | system-design | ml-ai | fullstack | papers
difficulty: medium        # easy | medium | hard
tags: [arrays, sliding-window]
sequence: 4               # optional; DSA uses this for syllabus order
---

# Your Note Title
```

---

## Deployment

Workflow: [`.github/workflows/daily-email.yml`](.github/workflows/daily-email.yml)

| Cron (UTC) | Days | IST | Command |
|------------|------|-----|---------|
| `47 1 * * 1-5` | Mon–Fri | 07:17 (arrives ~07:45–08:15) | `python agent/send_daily.py --mode daily` |

GitHub's scheduler is best-effort and sometimes runs late. Manual run: **Actions → daily-email → Run workflow** (choose `daily`, `learn`, or `quiz`).

Tests run on every code push to `main` via [`.github/workflows/tests.yml`](.github/workflows/tests.yml).

**Secrets** (Settings → Secrets and variables → Actions):

| Secret | Required | Source |
|--------|----------|--------|
| `RESEND_API_KEY` | Yes | [resend.com/api-keys](https://resend.com/api-keys) |
| `RECIPIENT` | Yes | Your inbox |
| `GEMINI_API_KEY` | Yes (for the quiz) | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

---

## Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `RESEND_API_KEY` | Yes | — | Email delivery |
| `RECIPIENT` | Yes | — | Destination address |
| `GEMINI_API_KEY` | Yes | — | Quiz, convert_notes, ingest_obsidian |
| `LLM_MODEL` | No | `gemini-flash-latest` | Override the Gemini model |

`gemini-flash-latest` is Google's alias for the newest Flash model, so retired model versions don't break the pipeline.

---

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

| Path | Role |
|------|------|
| `agent/send_daily.py` | Note selection, FSRS, quiz rotation, email rendering |
| `agent/llm_router.py` | Gemini client (OpenAI-compatible endpoint, retries) |
| `scripts/init_db.py` | Schema + migrate notes into SQLite |
| `scripts/convert_notes.py` | PDF/DOCX → study notes via Gemini |
| `scripts/ingest_obsidian.py` | Chunk large Obsidian guides into study notes via Gemini |
| `requirements.txt` | Runtime deps (daily email) |
| `requirements-dev.txt` | + conversion scripts and pytest |

---

## Roadmap

| Version | Status | Description |
|---------|--------|-------------|
| **MVP** | ✅ | Weighted pick, email delivery |
| **V1** | ✅ | SQLite FSRS, topic weights, Learn/Quiz split |
| **V1.1** | ✅ | Real passive FSRS (fsrs 6.x), DSA sequence, dry-run logging, tests |
| **V1.2** | ✅ | Gemini Flash, one combined weekday email, quiz rotation, tests in CI |
| **V1.5** | Planned | One-click Again/Hard/Good/Easy grading from the email |
| **V2** | Planned | Multi-user, OAuth, per-user FSRS |
