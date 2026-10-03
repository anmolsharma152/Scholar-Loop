# Project State — Scholar-Loop

## Project Summary

Scholar-Loop is an automated, spaced-repetition learning companion that delivers a single combined **Learn + Quiz** digest every weekday morning over a personal Markdown knowledge base via email. Built on Python 3.12, FSRS-6 (`fsrs` 6.x), Google Gemini Flash (`gemini-flash-latest`), Resend email delivery, and GitHub Actions automation with SQLite (`data/user.db`) state persistence.

## Current Development Phase

**Phase 1.2 (Gemini Flash Migration & Single Weekday Combined Digest) is COMPLETE.**
- **LLM Engine:** Migrated completely to Google Gemini Flash (`gemini-flash-latest` with `gemini-3.8-flash` backup) using Google's OpenAI-compatible endpoint with low reasoning effort. All dead Groq and OpenRouter references purged.
- **Combined Weekday Email:** Merged separate morning Learn and evening Quiz emails into 1 cohesive morning digest (Mon–Fri at 07:17 IST, arriving ~07:45–08:15 IST). Weekends are completely silent.
- **Digest Architecture:** Part 1 (Learn notes, ~1,500w cap, FSRS reviews first), Part 2 (Active recall quiz on past notes, 3–6 questions, weakest memory first), Part 3 (Segregated answers at bottom).
- **Non-Blocking Resilience:** If Gemini generation ever fails, the email still delivers the Learn notes with an in-email notice and raises a GitHub Actions warning annotation.
- **Quiz Rotation State:** Quiz rotation (`last_quizzed`) tracked separately without mutating FSRS memory scheduling.
- **CI/CD & Testing:** Dedicated `.github/workflows/tests.yml` runs 95 pytest suites on code pushes. Deprecated Node 20 actions updated to Node 24 (`actions/checkout@v5`, `actions/setup-python@v6`).
- **Dependencies & Repo Hygiene:** Cleaned up unused dependencies (`google-generativeai`, `resend`), pruned stale documentation, removed untracked bloat (`uv.lock`, empty folders).

## Active Milestone

**Milestone: Knowledge Base Ingestion & Deck Progression**
- Activating the raw Obsidian study guides (`knowledge/obsidian/`) via `scripts/ingest_obsidian.py`.
- Accelerating deck review pacing to cycle through the 223-note library.

## Current Status

- **CI/CD:** `.github/workflows/daily-email.yml` (weekday cron `47 1 * * 1-5`) and `.github/workflows/tests.yml` active on `main`.
- **Knowledge Base:** 223 notes across 5 active topics (`dsa`, `system-design`, `ml-ai`, `fullstack`, `papers`).
- **Tests:** 95/95 tests passing (`pytest tests/ -q`).
- **Git Branch:** `main`, clean working tree, passwordless SSH push enabled on both `anmol` and `omarchy` user profiles.
- **Secrets:** `GEMINI_API_KEY`, `RESEND_API_KEY`, `RECIPIENT` configured in GitHub Secrets.

## Architecture References

- `ARCHITECTURE.md` — Authoritative system architecture, data flows, and LLM design.
- `TASKS.md` — Master operational task matrix, phase roadmap, and explicit portfolio boundaries.
- `AGENTS.md` — Coding agent guidelines, engineering norms, and portfolio scope.
- `agent/send_daily.py` — Core digest generator, FSRS scheduler, Resend email pipeline.
- `agent/llm_router.py` — Gemini client with alias resolution and retry backoff.
- `data/user.db` — SQLite database storing FSRS state and review history.

## Core Constraints

- **Scope boundaries:** Scholar-Loop owns spaced repetition and knowledge digests only. No operator/task automation (Ozyman), no job scraping/LPA matching (Disha), no creative synthesis (IdeaForge).
- **Decoupled state:** State lives in `data/user.db`, never in markdown frontmatter.
- **Atomic git commits:** GitHub Actions commits `data/user.db` with `[skip ci]` to prevent recursive workflow loops.
- **Dry-run first:** Always test digest generation via `--dry-run` or `--preview` before triggering live Resend dispatches.

## Implemented Features

- FSRS-6 passive review engine with `Rating.Good` multi-day intervals.
- Dynamic word count cap ensuring 2–3 focused notes per digest.
- Single combined weekday morning email (Learn + Quiz + Answers).
- Active recall quiz rotation (least recently quizzed + lowest stability first; skips today's Learn notes).
- Defensive QA generation with Google Gemini Flash (`gemini-flash-latest`).
- Inlined CSS newsletter template with Gmail 102 KB clipping guards.
- Subject line topic synchronization and Oxford comma grammar rules.
- Local ingestion scripts: `scripts/convert_notes.py` (PDF/DOCX) and `scripts/ingest_obsidian.py` (Obsidian guide chunking) powered by Gemini.

## Features In Progress / Planned

- Ingesting raw Obsidian study guides (`knowledge/obsidian/ai-system-design-guide/`) into active topics.
- Custom sender domain on Resend (replacing `onboarding@resend.dev`).
- Interactive 1-click email grading links (`Again`, `Hard`, `Good`, `Easy`) directly updating FSRS state.

## Technical Debt / Known Issues

- **GitHub Actions Cron Queue Delays:** Native GitHub cron triggers are best-effort and can experience delays (30–60m typical) during high global runner traffic.
- **Deck Pace:** 40 of 223 notes have been introduced to date; at ~2 notes per weekday, a full pass takes ~9 months.

## Open Questions

1. When to begin batch-ingesting the Obsidian study guides into the active knowledge deck?
2. Should we increase daily note throughput (e.g. 3–4 notes) to accelerate library coverage?

## Next Three Recommended Tasks

1. Ingest initial batch of Obsidian system design guides into `knowledge/system-design/`.
2. Evaluate deck throughput / pacing settings in `agent/send_daily.py`.
3. Set up custom Resend sender domain.
