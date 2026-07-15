# Scholar-Loop — Project Plan

*Last updated: 2026-07-16*

---

## What It Is

A daily email newsletter that sends 2 study notes from your `knowledge/` base, enhanced by Groq LLM with recaps and quiz questions. Uses spaced repetition to track what's been sent and when to resend.

## What We're Building

Three versions, each deployable and useful on its own.

---

## V1 — Core Rebuild

**Goal**: Replace the monolithic `send_daily.py` (378 lines) with a modular system that uses FSRS instead of the hand-rolled scoring.

### What changes

| Area | Current | V1 |
|------|---------|-----|
| State | Frontmatter in each `.md` file | Single SQLite DB (`data/user.db`) |
| Algorithm | `score_note()`: `delta * 10 - rc * 5` | FSRS stability-based scheduling |
| Storage schema | YAML frontmatter | `notes`, `reviews`, `schedule` tables |
| Note ingestion | Manual markdown writing | `scripts/convert_notes.py` (PDF/DOCX → markdown) |
| CLI | `--dry-run`, `--topic`, `--reset-dsa` | `init`, `ingest`, `send`, `stats`, `reset` |
| Selection | Random weighted + sequence filter | FSRS next-review + topic diversity |
| Email templates | Inline HTML strings | Jinja2 templates (`templates/`) |
| Note format | Mixed sizes (134–3000+ words) | Standardized 400–600 words |

### Database schema (`data/user.db`)

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,       -- relative to knowledge/
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT,
    tags TEXT,                        -- JSON array
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    note_id INTEGER REFERENCES notes(id),
    sent_at TIMESTAMP NOT NULL,
    grade INTEGER NOT NULL,           -- 0-5 (FSRS scale)
    review_count INTEGER DEFAULT 0
);

-- FSRS state stored per note in the notes table:
-- stability REAL, difficulty REAL, due TIMESTAMP, elapsed_days INTEGER
```

### Scripts

```
scripts/
  init_db.py          # Create DB, migrate existing frontmatter state
  convert_notes.py    # PDF/DOCX → markdown with frontmatter
  send_daily.py       # Core email engine (replaces agent/send_daily.py)
  reset.py            # Reset note state (replaces --reset-dsa)
```

### Note conversion (`convert_notes.py`)

Not a pipeline — a one-time script. Takes a source directory, outputs markdown to `knowledge/<topic>/`.

**Input sources**:
- `~/Downloads/*.pdf` (40 new PDFs identified)
- `~/Downloads/Chiku Notes/*.docx` (36 files: 7 SQL, 11 Python/DS, 5 Viz, 7 Interview, 3 Cheatsheets, 3 Skip)
- `~/Downloads/*.docx` (25 DOCX files)

**Process**:
1. Extract text from PDF/DOCX
2. Send to Groq LLM: "Convert to a 400-600 word study note with YAML frontmatter"
3. Write to `knowledge/<topic>/`
4. Create DB entry

**Note size rules**:
- Target: 400-600 words (1 min read each × 2 = 2 min email)
- Minimum: 300 words (merge with related topic if shorter)
- Maximum: 800 words (LLM recap compresses for email anyway)

### FSRS integration

Use the `fsrs` Python package (maintained by Anki creator, battle-tested on millions of reviews).

**Reference paper**: `~/Downloads/FSRS_TKDE2023_Memory_Dynamics.pdf` — covers both SM-2 and FSRS algorithms.

**How FSRS replaces `score_note()`**:
- Each note has `stability`, `difficulty`, `due` in the DB
- When sent, grade is recorded (0-5 scale)
- FSRS computes next review date based on memory model
- Selection picks notes where `due <= now` (overdue notes first)

**Grade mapping** (for email newsletter context):
- 5: "I knew this cold" (perfect recall)
- 4: "Took a moment but got it"
- 3: "Struggled but remembered"
- 2: "Got it wrong initially"
- 1: "Complete blank, saw answer and recognized"
- 0: "No idea even after seeing answer"

Since this is email-based (no interactive quiz), we approximate grades:
- Default grade = 3 (recipient opened email, likely read both notes)
- Optional: track email opens via Resend webhooks → grade 4-5
- Optional: track click-through on quiz answers → grade 2-3

### Email templates

```
templates/
  email_wrapper.html    # Outer shell (header, footer, responsive CSS)
  note_section.html     # Single note block
  quiz_answer.html      # Spoiler answer block
```

### Topic diversity

Replace "pick from different topics" with FSRS-driven selection that ensures:
- At least 1 technical topic per email (DSA, system-design, SQL, fullstack)
- Max 1 paper per email
- No topic repeats within 3 emails

### CLI usage

```bash
# Setup
python scripts/init_db.py                          # Create DB, import existing state
python scripts/convert_notes.py ~/Downloads/*.pdf   # Convert PDFs
python scripts/convert_notes.py ~/Downloads/Chiku\ Notes/  # Convert DOCX

# Daily
python scripts/send_daily.py                       # Normal run
python scripts/send_daily.py --dry-run             # Preview
python scripts/send_daily.py --topic dsa           # Force topic

# Maintenance
python scripts/reset.py --topic dsa                # Reset one topic
python scripts/reset.py --all                      # Full reset
```

---

## V2 — Production

**Goal**: Reliable daily delivery with monitoring, error handling, and an admin dashboard.

### What's added

| Area | V1 | V2 |
|------|-----|-----|
| Delivery | Basic Resend send | Retry logic, delivery tracking, bounce handling |
| Monitoring | Print to stdout | Admin dashboard (Jinja2 + htmx) |
| State | SQLite only | SQLite + Git sync (push metadata updates) |
| Error handling | Try/except, exit | Graceful degradation, logging |
| Email | Plain HTML | Responsive, tested on 5+ email clients |
| Scheduling | GitHub Actions cron | GitHub Actions + manual trigger |
| Content | Notes only | Notes + "From the vault" (revisit old notes) |

### Admin dashboard

**Stack**: Jinja2 templates + htmx + vanilla CSS (no React, no framework).

**Purpose**: Admin/developer observability — NOT a student-facing learning interface.

**Pages**:
- `/` — Overview: notes count by topic, upcoming schedule, last 10 emails sent
- `/notes` — All notes with FSRS state (stability, difficulty, due date, review count)
- `/schedule` — Next 7 days of scheduled sends
- `/emails` — Log of sent emails with delivery status
- `/stats` — Charts: notes by topic, review frequency, LLM usage

**How it works**:
- Single `app.py` using Flask or FastAPI
- Templates in `templates/admin/`
- htmx for live updates (no page reloads)
- Runs locally or on a small VPS
- GitHub Actions sends emails; dashboard is read-only

### Delivery reliability

- Track send status in DB (`sent`, `delivered`, `bounced`, `complained`)
- Resend webhooks for delivery events
- Retry failed sends with exponential backoff
- Alert if 3+ consecutive failures

---

## V3 — Multi-User

**Goal**: Let other people sign up and get their own personalized emails.

### What's added

| Area | V2 | V3 |
|------|-----|-----|
| Users | Single user | Multi-user via Google OAuth |
| State | `data/user.db` | `data/users/<user_id>/db` per user |
| Auth | None | Google OAuth + session tokens |
| Content | Shared knowledge base | Per-user knowledge base + shared core |
| Dashboard | Admin only | Per-user progress view |
| Pricing | Free | Free tier + premium (more topics, custom schedules) |

### User model

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,              -- UUID
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    google_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings TEXT                     -- JSON: topics, schedule, timezone
);
```

### How multi-user works

- System always sends to user's email first
- Others can sign up via Google OAuth
- Each user gets their own SQLite DB with FSRS state
- Shared knowledge base (`knowledge/`) + per-user notes (optional)
- User controls: topics, frequency, time of day

---

## Migration from Current State

### What we're keeping
- `knowledge/` directory structure (7 topic dirs)
- All 193 committed notes
- GitHub Actions workflow (update paths)
- Resend + Groq API integration
- Email design (purple gradient, 850px)

### What we're replacing
- `agent/send_daily.py` → `scripts/send_daily.py`
- Frontmatter state → SQLite DB
- `score_note()` → FSRS
- Inline HTML templates → Jinja2

### What we're adding
- `scripts/` directory (CLI tools)
- `templates/` directory (Jinja2)
- `data/` directory (SQLite DBs, gitignored)
- `ingestion/` directory (note conversion scripts)
- `docs/project_plan.md` (this file)

### What we're archiving
- `knowledge/obsidian/` → `knowledge/archive/obsidian/` (150 files, preserved but invisible)
- `docs/consolidated_plan.md` → keep until V1 complete, then delete

---

## Execution Order

### V1 Sprint (current)
1. **Reset DSA metadata** — `segment-tree.md` `last_sent → null`, `review_count → 0`
2. **Create SQLite schema** — `scripts/init_db.py`
3. **Import existing state** — migrate frontmatter `last_sent`/`review_count` to DB
4. **Integrate FSRS** — install `fsrs` package, replace `score_note()`
5. **Note conversion** — `scripts/convert_notes.py` for 40 PDFs + 36 Chiku Notes
6. **Note resizing** — standardize all notes to 400-600 words
7. **Selection refactor** — FSRS-driven selection with topic diversity
8. **Email templates** — Jinja2 with responsive CSS
9. **CLI** — `init`, `ingest`, `send`, `stats`, `reset`
10. **Archive obsidian** — move to `knowledge/archive/obsidian/`

### V2 Sprint (after V1)
1. Admin dashboard
2. Delivery tracking
3. Error handling + logging
4. Email client testing
5. Git sync for metadata

### V3 Sprint (after V2)
1. Google OAuth
2. Multi-user DB architecture
3. User settings
4. Per-user customization

---

## Reference Materials

| File | Purpose |
|------|---------|
| `~/Downloads/FSRS_TKDE2023_Memory_Dynamics.pdf` | FSRS algorithm paper (primary reference) |
| `~/Downloads/SM2_Wozniak_1990_Thesis.html` | SM-2 original algorithm (classic Anki) |
| `~/Downloads/SM2_Algorithm.html` | SM-2 implementation docs |
| `https://github.com/open-spaced-repetition/fsrs-python` | FSRS Python package |
| `https://github.com/maimemo/SSP-MMC` | SSP-MMC spaced repetition (KDD 2022) |
