# Scholar-Loop — Architecture & System Design

Scholar-Loop is an automated, spaced-repetition learning companion designed to deliver structured **Learn** (morning curriculum) and **Quiz** (evening active recall) digests over a personal Markdown knowledge base via email.

---

## 1. System Overview & Core Philosophy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SCHOLAR-LOOP ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ Markdown Knowledge Base ] ───► [ SQLite State (data/user.db) ]            │
│  (YAML metadata + frontmatter)    (FSRS-6 Stability, Difficulty, Due Dates)  │
│                                           │                                 │
│                                           ▼                                 │
│                                [ agent/send_daily.py ]                      │
│                                           │                                 │
│                   ┌───────────────────────┴───────────────────────┐         │
│                   ▼                                               ▼         │
│         [ LEARN ENGINE (Morning) ]                      [ QUIZ ENGINE (Evening) ]   │
│         • Proportional topic slots                      • Partition-diverse pool   │
│         • Due notes first (NULLS LAST)                  • Groq LLM (Q1–Q3 / A1–A3) │
│         • Sequential syllabus gating                    • Newsletter solution box  │
│         • Dynamic word cap (~1500w)                     • Topic-synchronized subj  │
│         • FSRS Passive Good update                      • Zero state mutation      │
│                   │                                               │         │
│                   └───────────────────────┬───────────────────────┘         │
│                                           ▼                                 │
│                               [ Resend Email Delivery ]                     │
│                               (Inlined CSS via Premailer)                   │
│                                           │                                 │
│                                           ▼                                 │
│                                    [ User Inbox ]                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Tenets
1. **Decoupled State:** Markdown files contain content and static curriculum metadata (`topic`, `difficulty`, `sequence`). Dynamic scheduling state (stability, difficulty, due timestamps, review logs) lives exclusively in SQLite (`data/user.db`).
2. **Deterministic Syllabus Advancement:** DSA foundations advance strictly in sequential order (`sequence ASC`) to prevent prerequisites from being skipped.
3. **Active Recall over Passive Recognition:** Evening quizzes generate challenging conceptual questions up front and segregate solutions into a dedicated footer section.
4. **Resilient LLM Pipelines:** Strict prompt schemas paired with multi-layer defensive parsing (stripping reasoning tags, filtering template placeholders, deduplicating pairs, and handling 429 rate-limit backoffs).

---

## 2. Component Design & Data Flow

### A. Knowledge Base (`knowledge/`)
Markdown notes are organized into standardized topic domains:
- `dsa/`: Data structures, algorithms, and mathematical foundations with strict `sequence` ordering.
- `system-design/`: Distributed systems, architecture patterns, scalability, and consensus.
- `ml-ai/`: Deep learning, computer vision, NLP, transformers, and training techniques.
- `fullstack/`: Python internals, FastAPI, TypeScript, React, SQL, and database indexing.
- `papers/`: Concise research paper summaries (Transformer, FlashAttention, I-JEPA, DeepSeek).

**Frontmatter Schema:**
```yaml
---
topic: dsa                # dsa | system-design | ml-ai | fullstack | papers
difficulty: medium        # easy | medium | hard
tags: [hash-table, arrays]
sequence: 4               # integer syllabus order (mandatory for DSA curriculum)
---
```

---

### B. Scheduling Engine & State Machine (`agent/send_daily.py` + `data/user.db`)
Scholar-Loop integrates the **Free Spaced Repetition Scheduler (FSRS-6)**.

#### 1. Morning Learn Mode
- **Slot Allocation:** Proportional distribution across topics based on active weights.
- **Selection Priority:**
  - Due reviews are prioritized first using `ORDER BY due ASC NULLS LAST`.
  - Remaining word budget is filled with new sequential notes (`due IS NULL`).
- **Dynamic Word-Count Cap:** Enforces a ~1,500-word reading budget (minimum 2 notes) to guarantee consistent daily commitment without information overload.
- **State Mutation:** Sent notes receive a passive `Rating.Good` review via `_SCHEDULER.review_card()`, recalculating `stability`, `difficulty_fsrs`, and extending the next `due` date into the future.

#### 2. Evening Quiz Mode
- **Topic Diversity:** Selects 2–4 previously sent notes (`WHERE last_sent IS NOT NULL`) using window partitioning:
  ```sql
  ORDER BY ROW_NUMBER() OVER (PARTITION BY topic ORDER BY RANDOM()), RANDOM()
  ```
- **State Mutation:** Pure active recall. Does **not** mutate FSRS state or alter note review timestamps.

---

### C. LLM Active Recall & Defensive Parsing Engine

Evening quizzes call Groq's high-speed inference engine (`groq/compound-mini`).

```
[ Raw Note Markdown ] ──► [ Groq API ] ──► [ Defensive Parser ] ──► [ HTML Newsletter ]
                                            ├── Regex <think> strip
                                            ├── Schema regex match
                                            ├── Placeholder blacklist
                                            └── Deduplication set
```

#### 4-Layer Defensive Parser Architecture:
1. **`<think>` Tag Stripping:** Reasoning and thinking tokens (e.g. `<think>...</think>` from reasoning models) are stripped via regex before parsing.
2. **Strict Regex Matching:** Matches lines strictly conforming to `Q[1-3].` and `A[1-3].` prefixes.
3. **Placeholder Blacklist:** Explicitly drops hallucinated template placeholders (e.g. `[question text]`, `[concise answer]`).
4. **Deduplication:** Maintains `seen_q` and `seen_a` sets to ensure exactly 3 distinct questions and 3 distinct answers per note.
5. **Rate-Limit Retry Backoff:** Intercepts HTTP 429 errors, extracts the exact cooldown duration from Groq's response (e.g. `try again in 8.42s`), sleeps, and retries up to 3 times.

#### Newsletter Solution Layout:
- **Questions:** Displayed cleanly beneath note headers as `Q1.`, `Q2.`, `Q3.`.
- **Answers:** Segregated in a footer block as `A1:`, `A2:`, `A3:` beneath a dashed separation barrier.

---

### D. Subject Line & Grammar Engine
- **Topic Synchronization:** Subject lines dynamically compute topics solely from notes that *successfully passed generation and were included in the email body*.
- **2-Item Grammar Rule:** Formats 2-topic emails cleanly without an Oxford comma (`"DSA and ML"` instead of `"DSA, and ML"`), while preserving the Oxford comma for 3+ topics (`"DSA, ML, and System Design"`).

---

## 3. Scheduling Infrastructure & Reliability Analysis

### The Problem: GitHub Actions Native Cron Failure Mode
During production operations, native GitHub Actions `schedule:` triggers exhibited severe scheduling anomalies:
- **Shared Queue Delays:** Morning crons scheduled for 07:17 AM IST were queued and delayed by GitHub for **up to 10 hours**, dumping morning digests at 5:32 PM.
- **Dropped Crons:** During high global runner traffic, scheduled triggers were dropped entirely without execution or retry.

### The Solution: Decoupled Execution Clock
To achieve deterministic, to-the-minute delivery, the scheduling timer must be decoupled from GitHub Actions runners.

```
┌────────────────────────────────────────────────────────┐
│  EXTERNAL DEDICATED CLOCK                              │
│  (AWS EventBridge / Cron-Job.org)                      │
│  Fires at EXACTLY 07:45:00 AM & 03:45:00 PM IST        │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ HTTP POST /repos/.../dispatches
                            │ Headers: { Authorization: Bearer <PAT> }
                            ▼
┌────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS (repository_dispatch)                  │
│  Spins up in 15–20s; runs send_daily.py; commits DB    │
└────────────────────────────────────────────────────────┘
```

### Architectural Comparison of Scheduling Solutions

| Dimension | Native GitHub Cron | cron-job.org Webhook | AWS EventBridge (Path A) | AWS Serverless (Path B) |
| :--- | :---: | :---: | :---: | :---: |
| **Trigger Precision** | Unreliable (0–10h lag) | Exact Second | Exact Second | Exact Second |
| **SLA / Uptime** | Best-effort (no SLA) | 99.9% | 99.999% (Multi-AZ) | 99.999% |
| **Secret Security** | Repo Secrets | SaaS Database | AWS Secrets Manager / IAM | AWS Secrets Manager / IAM |
| **Observability** | Action Run History | Web Dashboard | CloudWatch Logs & DLQ | CloudWatch & X-Ray |
| **Code Changes** | None | Add `repository_dispatch` | Add `repository_dispatch` | Rewrite for Lambda + S3 |
| **Resume Weight** | Baseline | Low | **High (AWS Cloud)** | **Maximum (Full Serverless)** |
| **Cost** | Free | Free | Free ($0.00 / 14M tier) | Free ($0.00 / Free Tier) |

---

## 4. Portfolio Boundaries & Product Charter

Scholar-Loop operates within a distinct functional boundary among sibling projects:

| Project | Dedicated Domain | Explicit Boundary (Out of Scope for Scholar-Loop) |
| :--- | :--- | :--- |
| **Scholar-Loop** | **Spaced-Repetition Learning Companion** | No mailbox management, no job board scraping, no creative synthesis. |
| **Ozyman** | Autonomous Operator / Task Agent | Handles Gmail/GitHub triage, background automation, and operational tasks. |
| **Disha** | Career Intelligence & Job Matching | Handles resume scoring, job scraping, LPA fit, and market analytics. |
| **IdeaForge** | Creative Synthesis & Idea OS | Handles divergence-evaluation idea generation and brainstorming. |

---

## 5. Security & Data Hygiene Norms

- **Zero Secret Leaks:** API keys (`RESEND_API_KEY`, `GROQ_API_KEY`, GitHub PATs) are never committed to git.
- **Atomic Commits:** Scheduled runs commit `data/user.db` updates with `[skip ci]` to prevent recursive CI loops.
- **Binary Merge Hygiene:** In case of remote FSRS state conflicts, always favor the remote bot state (`git checkout --theirs data/user.db`).
