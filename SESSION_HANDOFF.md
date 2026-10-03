# Session Handoff — Scholar-Loop

## Current Work Session

- Resumed session on 2026-10-03.
- **Root Cause & Fix for 11-Day Quiz Outage:** Investigated failed evening runs (broken since Sept 22 due to Groq decommissioning models). Completely replaced Groq with Google Gemini Flash (`gemini-flash-latest` / `gemini-3.8-flash`).
- **Inbox Fatigue & Architecture Shift:** Addressed user disengagement from 2 daily emails (14/week). Transitioned to a single combined **Learn + Quiz morning digest** sent Monday through Friday only (`cron: '47 1 * * 1-5'`). Weekends are 100% silent.
- **Repository Audit & Cleanup:**
  - Removed all dead Groq, OpenRouter, Llama, Qwen, and Compound references across `agent/llm_router.py`, `agent/send_daily.py`, `scripts/convert_notes.py`, `scripts/ingest_obsidian.py`, and documentation.
  - Trimmed `requirements.txt` (removed unused `resend` and deprecated `google-generativeai`). Created `requirements-dev.txt` for conversion tools and pytest.
  - Fixed 4 broken tests in `tests/test_make_subject.py` and `tests/test_run_quiz.py`. Added comprehensive `tests/test_run_daily.py` (95/95 tests passing).
  - Added `.github/workflows/tests.yml` to run pytest automatically on pushes to `main`.
  - Upgraded GitHub Actions to Node 24 (`actions/checkout@v5`, `actions/setup-python@v6`).
  - Pruned empty folders (`tools/`, `templates/`, `ingestion/`), deleted untracked `uv.lock`, and deleted stale legacy markdown in `docs/`.
  - Configured `GEMINI_API_KEY` secret in GitHub repository via `gh secret set` and purged `GROQ_API_KEY`.

## What Was Completed

- `agent/llm_router.py` rewritten to use Gemini OpenAI-compatible endpoint with `gemini-flash-latest`, low reasoning effort, and rate-limit backoff.
- `agent/send_daily.py` updated with `run_daily`:
  - Part 1: Learn notes (~1,500w cap, FSRS reviews first).
  - Part 2: Active recall quiz on past notes (3–6 questions, weakest memory first; skips today's Learn notes).
  - Part 3: Segregated answers footer.
  - Soft-fail resilience: if Gemini ever fails, Learn notes still send with an in-email notice and GitHub warning annotation.
  - Gmail clipping guard (< 102 KB).
  - CLI updated: `--mode daily` is default; added `--preview <file>`.
- Full live preview verified: 27.8 KB HTML generated without mutating database or FSRS state.
- Documentation refreshed: `README.md`, `docs/setup.md`, `AGENTS.md`, `PROJECT_STATE.md`, `SESSION_HANDOFF.md`, `.env.example`.

## Files Touched This Session

- `agent/llm_router.py` (rewritten for Gemini)
- `agent/send_daily.py` (combined daily digest, quiz rotation, CLI)
- `scripts/convert_notes.py` (Gemini key check)
- `scripts/ingest_obsidian.py` (Gemini key check)
- `.github/workflows/daily-email.yml` (weekday cron, Gemini secret)
- `.github/workflows/tests.yml` (new CI workflow for tests)
- `requirements.txt` & `requirements-dev.txt` (cleaned and split)
- `.python-version` (pinned 3.12)
- `tests/test_make_subject.py` & `tests/test_run_quiz.py` (fixed)
- `tests/test_run_daily.py` (new tests)
- `README.md`, `docs/setup.md`, `AGENTS.md`, `PROJECT_STATE.md`, `SESSION_HANDOFF.md`, `.env.example`
- Deleted stale docs in `docs/`

## Important Decisions

- **Single Weekday Email:** 5 emails/week (Mon–Fri ~07:45–08:15 IST). Cuts inbox volume in half while preserving FSRS spaced repetition integrity. Notes due over the weekend wait until Monday.
- **Gemini Flash Latest Alias:** Uses `gemini-flash-latest` so future model version transitions by Google are automatic.
- **Fail-Safe Delivery:** LLM outages never block daily reading notes.
- **Zero CLI Toggle Complexity:** Kept configuration in code/workflow without adding unneeded toggle scripts.

## Current Blockers / Constraints

- None. All 95 tests pass, live Gemini generation verified, secrets set.

## Immediate Next Action

1. Commit and push the changes to `main`.
2. Dispatch a live test via `gh workflow run daily-email.yml -f mode=daily` to confirm inbox delivery.
