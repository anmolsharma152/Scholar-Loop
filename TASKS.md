# Scholar-Loop — Engineering Tasks & Roadmap

Comprehensive tracking of completed milestones, in-progress priorities, and future technical roadmap items.

---

## 🎯 Phase 1: Core Stabilization & Digest UX (Delivered ✅)

- [x] **FSRS-6 Mathematical Scheduler:** Full implementation of FSRS spaced repetition updating stability, difficulty, and next due date on SQLite (`data/user.db`).
- [x] **DSA Sequential Syllabus Gate:** Enforce strict prerequisites on algorithmic notes using `sequence ASC` ordering.
- [x] **Reviews-First Priority:** Prioritize overdue reviews over new syllabus notes using `ORDER BY due ASC NULLS LAST`.
- [x] **Dynamic Digest Length Cap:** Prevent cognitive overload with a ~1,500-word daily reading budget (minimum 2 notes).
- [x] **LLM Model Migration (`groq/compound-mini`):** Replaced deprecated models with Groq's high-speed, structured completion engine.
- [x] **4-Layer Defensive QA Parser:**
  - [x] Strip `<think>...</think>` tags from reasoning models via regex.
  - [x] Strict regex matching for `Q[1-3].` and `A[1-3].`.
  - [x] Blacklist placeholder hallucinations (`[question text]`, `[concise answer]`).
  - [x] Deduplication sets (`seen_q`, `seen_a`).
  - [x] Automated 429 rate-limit backoff extraction and retry loop.
- [x] **Active Recall Newsletter UX:** Display questions at the top (`Q1–Q3`) and segregate solutions (`A1–A3`) into a styled footer section.
- [x] **Subject Line Polish:**
  - [x] Fix 2-topic grammar (`"DSA and ML"` without extraneous Oxford comma).
  - [x] Synchronize subject topics strictly with delivered digest content.
- [x] **Repository Documentation:** Complete rewrite of `README.md`, `docs/STATUS.md`, and `docs/setup.md`.
- [x] **GitHub Metadata:** Live update of repository description and 13 targeted topics via `gh` CLI.

---

## 🚨 Phase 2: Decoupled Scheduler & Reliability (Immediate / P0)

- [ ] **Workflow Dispatch Update:**
  - [ ] Add `repository_dispatch: types: [learn, quiz]` to `.github/workflows/daily-email.yml`.
  - [ ] Remove flaky native `schedule:` crons from `.github/workflows/daily-email.yml` to prevent 10-hour queue delays.
- [ ] **External Clock Setup (Choose one):**
  - [ ] **Option A (AWS EventBridge):** Configure AWS EventBridge Scheduler rule sending authenticated POST requests to GitHub `dispatches` API at `07:45 AM` and `03:45 PM IST`.
  - [ ] **Option B (cron-job.org):** Configure 2 scheduled jobs sending authenticated POST requests to GitHub `dispatches` API.
- [ ] **Fine-Grained GitHub PAT:** Issue personal access token with `Actions: Read and write` permissions for webhook authentication.
- [ ] **Live Webhook Verification:** Validate end-to-end webhook trigger latency (< 30s execution).

---

## 📚 Phase 3: Ingestion Pipeline & Deck Expansion (Near-Term / P1)

- [ ] **Obsidian Knowledge Base Ingestion:**
  - [ ] Execute `scripts/ingest_obsidian.py` on `knowledge/obsidian/ai-system-design-guide/` (17 deep guides).
  - [ ] Execute `scripts/ingest_obsidian.py` on `knowledge/obsidian/interview-questions/` (5 topic areas).
  - [ ] Register new directories into `TOPIC_DIRS` in `scripts/init_db.py`.
- [ ] **Automated Research Paper Ingestion:**
  - [ ] Streamline `scripts/convert_notes.py` for direct arXiv PDF URLs and local research paper conversion into `knowledge/papers/`.
- [ ] **Custom Resend Sender Domain:**
  - [ ] Verify personal domain DNS records on Resend (replace `onboarding@resend.dev` with `digest@yourdomain.com`).

---

## ☁️ Phase 4: Advanced Features & Cloud Architecture (Medium-Term / P2)

- [ ] **Active 1-Click Email Grading:**
  - [ ] Embed one-click rating links (`Again`, `Hard`, `Good`, `Easy`) inside email footers.
  - [ ] Deploy lightweight webhook endpoint to record explicit user grade into FSRS state.
- [ ] **AWS Pure Serverless Migration (Path B):**
  - [ ] Containerize `send_daily.py` into AWS Lambda (Python 3.12).
  - [ ] Migrate SQLite `user.db` snapshot storage and retrieval to Amazon S3.
  - [ ] Manage API keys and credentials in AWS Secrets Manager.
  - [ ] Implement CloudWatch alarms and Dead Letter Queues (DLQ) for failed runs.

---

## 🚫 Explicit Non-Goals (Portfolio Demarcation)

The following capabilities belong to sibling projects and must **not** be absorbed into Scholar-Loop:
- **Gmail/GitHub Operator & Triage:** Handled exclusively by **Ozyman**.
- **Job Scraping & LPA Scoring:** Handled exclusively by **Disha**.
- **Creative Synthesis & Ideation:** Handled exclusively by **IdeaForge**.
