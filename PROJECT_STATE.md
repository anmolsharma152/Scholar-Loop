# Project State — Scholar-Loop

## Project Summary

Scholar-Loop is an automated, spaced-repetition learning companion designed to deliver structured **Learn** (morning curriculum) and **Quiz** (evening active recall) digests over a personal Markdown knowledge base via email. It is built on Python 3.12, the FSRS-6 scheduler (`fsrs` 6.x), Groq LLM inference (`groq/compound-mini`), Resend for email delivery, and GitHub Actions automation with SQLite (`data/user.db`) state persistence.

## Current Development Phase

**Phase 1 (Core Stabilization & Digest UX) is COMPLETE.**
- FSRS-6 mathematical scheduling running on SQLite (`stability`, `difficulty_fsrs`, `due`, `reviews`).
- DSA sequential curriculum gating (`sequence ASC`) preventing prerequisite skipping.
- Review prioritization over new notes (`due ASC NULLS LAST`).
- Dynamic digest length cap (~1,500 words, minimum 2 notes).
- Groq model migration to `groq/compound-mini` with a 4-layer defensive parser (`<think>` stripping, regex schema validation, placeholder blacklisting, deduplication, and 429 backoff retries).
- Active recall newsletter UX: `Q1–Q3` questions at the top, `A1–A3` solutions segregated in a footer block.
- Subject line polish: dynamic topic synchronization and 2-topic grammar formatting without extraneous Oxford commas (`"DSA and ML"`).

**Phase 2 (Scheduling Reliability & Ingestion) is IN PROGRESS / PENDING DECISION:**
- Still running on **GitHub Actions native dual cron** (`47 1 * * *` Learn, `47 9 * * *` Quiz).
- The planned transition to an external decoupled scheduler (AWS EventBridge Path A / cron-job.org via `repository_dispatch`) has **not** been applied yet; GitHub Actions CI/CD remains the active execution driver.

## Active Milestone

**Milestone: Operational Stabilization & Knowledge Base Expansion**
- Monitoring live morning/evening digests.
- Evaluating external trigger integration vs continuing with native GitHub Actions.
- Ingestion pipeline ready (`scripts/ingest_obsidian.py`) for raw study guides in `knowledge/obsidian/`.

## Current Status

- **CI/CD:** GitHub Actions workflow `.github/workflows/daily-email.yml` active on `main`.
- **Knowledge Base:** 223 notes across 5 active topics (`dsa`, `system-design`, `ml-ai`, `fullstack`, `papers`).
- **Tests:** `pytest tests/ -q` passes.
- **Git Branch:** `main`, clean working tree, passwordless SSH push enabled on both `anmol` and `omarchy` user profiles.

## Architecture References

- `ARCHITECTURE.md` — Authoritative system architecture, data flows, defensive LLM pipeline, and scheduling reliability analysis.
- `TASKS.md` — Master operational task matrix, phase roadmap, and explicit portfolio boundaries.
- `AGENTS.md` — Coding agent guidelines, engineering norms, and portfolio scope.
- `agent/send_daily.py` — Core digest generator, FSRS scheduler, Resend email pipeline.
- `data/user.db` — SQLite database storing FSRS state and review history.

## Core Constraints

- **Scope boundaries:** Scholar-Loop owns spaced repetition and knowledge digests only. No operator/task automation (Ozyman), no job scraping/LPA matching (Disha), no creative synthesis (IdeaForge).
- **Decoupled state:** State lives in `data/user.db`, never in markdown frontmatter.
- **Atomic git commits:** GitHub Actions commits `data/user.db` with `[skip ci]` to prevent recursive workflow loops.
- **Dry-run first:** Always test digest generation via `--dry-run` before triggering live Resend dispatches.

## Implemented Features

- FSRS-6 passive review engine with `Rating.Good` multi-day intervals.
- Dynamic word count cap ensuring 2–3 focused notes per digest.
- Defensive QA generation with Groq `groq/compound-mini`.
- Active recall newsletter email template with inlined CSS (`premailer`).
- Subject line topic synchronization and Oxford comma grammar rules.
- Local ingestion scripts: `scripts/convert_notes.py` (PDF/DOCX) and `scripts/ingest_obsidian.py` (Obsidian guide chunking).

## Features In Progress

- Decoupled clock trigger evaluation: Moving from native GitHub cron to an external scheduler (AWS EventBridge or cron-job.org via `repository_dispatch`) to eliminate GitHub runner queue delays.
- Obsidian knowledge base ingestion: Processing the 17 raw guides in `knowledge/obsidian/ai-system-design-guide/`.

## Pending Features

- Custom sender domain on Resend (replacing `onboarding@resend.dev`).
- Interactive 1-click email grading links (`Again`, `Hard`, `Good`, `Easy`) directly updating FSRS state.
- Pure serverless AWS migration (Path B: EventBridge + Lambda + S3).

## Recently Modified Areas

- `ARCHITECTURE.md` & `TASKS.md` authored and committed (`f7914a8`).
- `README.md`, `docs/STATUS.md`, and `docs/setup.md` synchronized with current FSRS rules, newsletter formatting, and cron times.
- GitHub repository description and 13 topics updated live via `gh` CLI.
- Passwordless SSH passphrase removed for seamless git pushes.

## Technical Debt / Known Issues

- **GitHub Actions Cron Queue Delays:** Native GitHub cron triggers are best-effort and can experience delays (up to several hours) during high global runner traffic.
- **Untracked `uv.lock`:** Exists locally from `uv` runs; needs decision on tracking or adding to `.gitignore`.

## Open Questions

1. When to pull the trigger on decoupling the cron trigger via `repository_dispatch` (AWS EventBridge vs cron-job.org)?
2. When to begin batch-ingesting the Obsidian study guides into the active knowledge deck?

## Next Three Recommended Tasks

1. Update `.github/workflows/daily-email.yml` to support `repository_dispatch` alongside `workflow_dispatch` and `schedule`.
2. Run `scripts/ingest_obsidian.py` on selected guides in `knowledge/obsidian/` to expand the active curriculum.
3. Clean up `uv.lock` (either add to `.gitignore` or track).
