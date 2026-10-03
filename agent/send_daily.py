#!/usr/bin/env python3
"""Scholar-Loop email: FSRS-driven note selection with an LLM-generated active-recall quiz.

The scheduled run sends ONE combined email (Learn notes + Quiz + Answers) on weekday
mornings. The standalone learn/quiz modes are kept for previews and debugging.

Usage:
  python agent/send_daily.py                             # daily (combined Learn + Quiz)
  python agent/send_daily.py --dry-run                   # preview the daily email without sending
  python agent/send_daily.py --mode learn                # Learn notes only
  python agent/send_daily.py --mode quiz                 # Quiz only
"""

import math
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import frontmatter
import markdown
from fsrs import Card, Rating, Scheduler, State
from premailer import transform


KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "user.db"

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RECIPIENT = os.environ.get("RECIPIENT")

TOPIC_WEIGHTS = {
    "dsa": 0.28,
    "ml-ai": 0.22,
    "papers": 0.20,
    "system-design": 0.16,
    "fullstack": 0.14,
}

NOTES_PER_LEARN = 4
NOTES_PER_QUIZ = 4          # standalone --mode quiz
NOTES_PER_DAILY_QUIZ = 2    # quiz section inside the combined daily email (3-6 questions)
MAX_NOTES_TOTAL = 5
GMAIL_CLIP_BYTES = 102 * 1024  # Gmail hides anything past ~102 KB of HTML

# Daily email has no intra-day learning steps — each send is one full review.
# Empty learning_steps so Rating.Good graduates straight to multi-day intervals.
_SCHEDULER = Scheduler(learning_steps=(), relearning_steps=(), enable_fuzzing=False)

HEADER_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; margin:0; padding:40px 20px; background-color:#f3f4f6; }}
  .container {{ max-width:850px; margin:0 auto; }}
  .header {{ background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%); border-radius:16px 16px 0 0; padding:40px; text-align:center; }}
  .header h1 {{ color:#fff; margin:0; font-size:32px; font-weight:800; letter-spacing:-0.025em; }}
  .header p {{ color:#c4b5fd; margin:8px 0 0; font-size:16px; font-weight:500; }}
  .body {{ background:#fff; padding:40px; border-radius:0 0 16px 16px; box-shadow:0 10px 15px -3px rgba(0,0,0,0.1); }}
  .footer {{ text-align:center; padding-top:30px; }}
  .footer p {{ font-size:14px; color:#6b7280; font-weight:500; }}
  .note-section {{ margin-bottom:40px; padding-bottom:40px; border-bottom:1px solid #e5e7eb; }}
  .note-section:last-child {{ border-bottom:none; margin-bottom:0; padding-bottom:0; }}
  .meta-row {{ display:flex; align-items:center; gap:10px; margin-bottom:16px; }}
  .tag-topic {{ font-size:12px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:#4f46e5; background:#e0e7ff; padding:4px 10px; border-radius:6px; }}
  .tag-diff {{ font-size:12px; font-weight:600; text-transform:uppercase; color:#6b7280; background:#f3f4f6; padding:4px 10px; border-radius:6px; }}
  h2 {{ margin:0 0 20px 0; font-size:26px; font-weight:800; color:#111827; line-height:1.3; }}
  .content {{ color:#374151; font-size:16px; line-height:1.7; }}
  .content pre {{ background:#f3f4f6; color:#1f2937; padding:16px; border-radius:8px; overflow-x:auto; font-size:14px; }}
  .content code {{ background:#f3f4f6; padding:2px 6px; border-radius:4px; font-size:14px; color:#1f2937; }}
  .content table {{ border-collapse:collapse; width:100%; margin:16px 0; }}
  .content th, .content td {{ border:1px solid #e5e7eb; padding:8px 12px; text-align:left; font-size:14px; }}
  .content th {{ background:#f9fafb; font-weight:700; }}
  .quiz-q {{ font-weight:700; color:#111827; margin:16px 0 4px; }}
  .quiz-answer {{ background:#f0fdf4; border-left:4px solid #22c55e; border-radius:0 8px 8px 0; padding:12px 16px; margin:4px 0 24px; font-size:15px; line-height:1.6; }}
  .answer-label {{ font-weight:700; color:#15803d; }}
  .part-heading {{ font-size:13px; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:#7c3aed; margin:0 0 24px; padding-bottom:10px; border-bottom:2px solid #ede9fe; }}
  .part-intro {{ color:#6b7280; font-size:15px; margin:-12px 0 24px; }}
  .quiz-part {{ margin-top:48px; padding-top:8px; }}
  .notice {{ background:#fffbeb; border-left:4px solid #f59e0b; border-radius:0 8px 8px 0; padding:12px 16px; color:#92400e; font-size:15px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Scholar-Loop</h1>
    <p>{date}</p>
  </div>
  <div class="body">
    {body}
  </div>
  <div class="footer">
    <p>Daily learning, built on spaced repetition.</p>
  </div>
</div>
</body>
</html>"""

NOTE_SELECT_COLS = """id, path, title, topic, difficulty, tags, word_count,
                   stability, difficulty_fsrs, due, review_count, last_sent,
                   sequence, state, step"""


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Create tables if needed and add FSRS state columns on older DBs."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT,
            tags TEXT,
            word_count INTEGER,
            sequence INTEGER,
            stability REAL DEFAULT 1.0,
            difficulty_fsrs REAL DEFAULT 3.0,
            due TEXT,
            elapsed_days INTEGER DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            last_sent TEXT,
            state INTEGER DEFAULT 1,
            step INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER REFERENCES notes(id),
            sent_at TEXT NOT NULL,
            grade INTEGER NOT NULL,
            response_time_ms INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_notes_topic ON notes(topic);
        CREATE INDEX IF NOT EXISTS idx_notes_due ON notes(due);
        CREATE INDEX IF NOT EXISTS idx_reviews_note ON reviews(note_id);
    """)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(notes)")}
    if "state" not in cols:
        conn.execute("ALTER TABLE notes ADD COLUMN state INTEGER DEFAULT 1")
    if "step" not in cols:
        conn.execute("ALTER TABLE notes ADD COLUMN step INTEGER")
    # Quiz rotation timestamp. Not FSRS state: quizzes never change scheduling.
    if "last_quizzed" not in cols:
        conn.execute("ALTER TABLE notes ADD COLUMN last_quizzed TEXT")
    # Heal legacy rows that were "reviewed" without real FSRS graduation.
    conn.execute("""
        UPDATE notes
        SET state = 2, step = NULL
        WHERE last_sent IS NOT NULL
          AND review_count > 0
          AND (state IS NULL OR state = 1)
    """)
    conn.commit()


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn


def count_due(conn, topic: str, now: datetime | None = None) -> int:
    if now is None:
        now = datetime.now(timezone.utc)
    return conn.execute(
        "SELECT COUNT(*) FROM notes WHERE topic=? AND (due IS NULL OR due <= ?)",
        (topic, now.isoformat())
    ).fetchone()[0]


def _apply_sequence_filter(
    conn: sqlite3.Connection,
    topic: str,
    rows: list[sqlite3.Row],
) -> list[sqlite3.Row]:
    """Gate brand-new notes by curriculum sequence when the topic uses it.

    Already-sent (review) notes pass through. Unsent notes are only eligible
    at the minimum sequence among unsent notes for that topic. Notes without
    a sequence tag are never blocked.
    """
    min_seq = conn.execute(
        """SELECT MIN(sequence) FROM notes
           WHERE topic=? AND last_sent IS NULL AND sequence IS NOT NULL""",
        (topic,),
    ).fetchone()[0]
    if min_seq is None:
        return rows

    filtered: list[sqlite3.Row] = []
    for r in rows:
        if r["last_sent"] is not None:
            filtered.append(r)
        elif r["sequence"] is None or r["sequence"] == min_seq:
            filtered.append(r)
    return filtered


def pick_due_notes(conn, topic: str, count: int, exclude_ids: set = None,
                   now: datetime | None = None) -> list[sqlite3.Row]:
    if now is None:
        now = datetime.now(timezone.utc)
    if exclude_ids is None:
        exclude_ids = set()

    exclude_clause = ""
    params: list = [topic, now.isoformat()]
    if exclude_ids:
        placeholders = ",".join("?" for _ in exclude_ids)
        exclude_clause = f" AND id NOT IN ({placeholders})"
        params.extend(exclude_ids)

    # No LIMIT before sequence filter — gate may drop many unsent candidates.
    rows = conn.execute(
        f"""SELECT {NOTE_SELECT_COLS}
            FROM notes
            WHERE topic=? AND (due IS NULL OR due <= ?)
            {exclude_clause}
            ORDER BY
              due ASC NULLS FIRST,
              sequence ASC NULLS LAST,
              RANDOM()""",
        params,
    ).fetchall()

    rows = _apply_sequence_filter(conn, topic, rows)

    # Curriculum topics: prefer introducing the current sequence step over
    # replaying older out-of-order reviews, so the syllabus can advance.
    min_seq = conn.execute(
        """SELECT MIN(sequence) FROM notes
           WHERE topic=? AND last_sent IS NULL AND sequence IS NOT NULL""",
        (topic,),
    ).fetchone()[0]
    if min_seq is not None:
        rows = sorted(
            rows,
            key=lambda r: (
                0 if r["last_sent"] is None else 1,
                r["due"] or "",
                r["sequence"] if r["sequence"] is not None else 10**9,
            ),
        )
    else:
        # No curriculum: prefer due reviews before brand-new notes.
        rows = sorted(
            rows,
            key=lambda r: (
                0 if r["last_sent"] is not None else 1,
                r["due"] or "",
            ),
        )

    return list(rows[:count])


def compute_retrievability(stability: float, difficulty: float,
                           last_sent: str | None,
                           now: datetime | None = None) -> float:
    if now is None:
        now = datetime.now(timezone.utc)
    if not last_sent or stability <= 0:
        return 0.0
    last = _parse_dt(last_sent)
    if last is None:
        return 0.0
    elapsed_days = (now - last).total_seconds() / 86400.0
    if elapsed_days < 0:
        elapsed_days = 0
    # Simplified exponential forgetting: R = 2^(-elapsed / stability)
    decay = math.pow(2.0, -elapsed_days / max(stability, 0.01))
    return max(decay, 0.0)


def _card_from_row(row: sqlite3.Row) -> Card:
    """Rebuild an fsrs Card from a notes row (fsrs 6.x fields)."""
    review_count = row["review_count"] or 0
    last = _parse_dt(row["last_sent"])

    if not last or review_count <= 0:
        return Card()

    due = _parse_dt(row["due"]) or last
    try:
        state_raw = row["state"]
    except (IndexError, KeyError):
        state_raw = None
    try:
        step = row["step"]
    except (IndexError, KeyError):
        step = None

    # Legacy rows without state: treat as Review so Good advances multi-day.
    if state_raw is None:
        state = State.Review
    else:
        state = State(int(state_raw))

    stability = row["stability"]
    difficulty = row["difficulty_fsrs"]
    return Card(
        state=state,
        step=step,
        stability=float(stability) if stability is not None else None,
        difficulty=float(difficulty) if difficulty is not None else None,
        due=due,
        last_review=last,
    )


def mark_sent(conn, note_id: int, now: datetime | None = None):
    """Record a passive Good review and schedule the next due date via FSRS."""
    if now is None:
        now = datetime.now(timezone.utc)

    row = conn.execute(
        f"SELECT {NOTE_SELECT_COLS} FROM notes WHERE id=?",
        (note_id,),
    ).fetchone()
    if not row:
        return

    card = _card_from_row(row)
    card, _ = _SCHEDULER.review_card(card, Rating.Good, now)
    new_count = (row["review_count"] or 0) + 1

    conn.execute(
        """UPDATE notes SET last_sent=?, review_count=?, due=?,
               stability=?, difficulty_fsrs=?, state=?, step=?
           WHERE id=?""",
        (
            now.isoformat(),
            new_count,
            card.due.isoformat(),
            card.stability,
            card.difficulty,
            int(card.state),
            card.step,
            note_id,
        ),
    )
    conn.execute(
        "INSERT INTO reviews (note_id, sent_at, grade) VALUES (?, ?, ?)",
        (note_id, now.isoformat(), int(Rating.Good)),
    )
    conn.commit()


def read_note_content(path: str) -> str:
    full = KNOWLEDGE_DIR.parent / path
    if not full.exists():
        return ""
    post = frontmatter.load(str(full))
    return post.content


def extract_title(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def strip_h1(content: str) -> str:
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("# "):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            return "\n".join(lines[:i] + lines[j:])
    return content


def render_markdown(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=["fenced_code", "tables", "nl2br", "sane_lists", "md_in_html"],
    )


def format_note_section(row, content_html: str) -> str:
    topic = row["topic"]
    diff = row["difficulty"] or "medium"
    return f"""<div class="note-section">
  <div class="meta-row">
    <span class="tag-topic">{topic}</span>
    <span class="tag-diff">{diff}</span>
  </div>
  <h2>&#x1F4DD; {row["title"]}</h2>
  <div class="content">{content_html}</div>
</div>"""


def generate_quiz_qas(content: str, title: str, topic: str) -> tuple[str, str] | None:
    try:
        # Import fallback router (handles sys.path dynamically)
        try:
            from agent.llm_router import chat_completion_with_fallback
        except ImportError:
            from llm_router import chat_completion_with_fallback
    except Exception as e:
        print(f"  [warn] failed to import llm_router: {e}", file=sys.stderr)
        return None

    prompt = f"""You are a quiz generator. Given the following study note, generate EXACTLY 3 quiz questions that test understanding of the key concepts.

Each question must follow this exact format:

Q1. [question text]
A1. [concise answer]

Q2. [question text]
A2. [concise answer]

Q3. [question text]
A3. [concise answer]

Rules:
- Questions must be answerable from the note content alone.
- Answers must be factual, specific, and 1-3 sentences.
- Do NOT include the questions' answers anywhere else in the output.
- Output only the 3 Q&A pairs, nothing else.

Note title: {title}
Topic: {topic}

Note content:
{content[:4000]}
"""
    try:
        result, provider, model = chat_completion_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )

        # Parse Q1/A1 format — take only first 3 unique, non-placeholder pairs
        questions_html = []
        answers_html = []
        seen_q: set = set()
        seen_a: set = set()

        for line in result.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Match "Q1. ..." style lines
            if line.startswith("Q") and len(line) > 3 and line[1].isdigit() and line[2] == ".":
                text = line[3:].strip()
                if text in ("[question text]", "[text]", "") or text.startswith("["):
                    continue
                if text not in seen_q and len(questions_html) < 3:
                    seen_q.add(text)
                    questions_html.append(f'<div class="quiz-q"><strong>Q{len(questions_html)+1}.</strong> {text}</div>')
            # Match "A1. ..." style lines
            elif line.startswith("A") and len(line) > 3 and line[1].isdigit() and line[2] == ".":
                text = line[3:].strip()
                if text in ("[concise answer]", "[answer]", "...", "") or text.startswith("["):
                    continue
                if text not in seen_a and len(answers_html) < 3:
                    seen_a.add(text)
                    answers_html.append(f'<div class="quiz-answer"><strong>A{len(answers_html)+1}:</strong> {text}</div>')

        if not questions_html or not answers_html:
            return None

        return "\n".join(questions_html), "\n".join(answers_html)

    except Exception as e:
        print(f"  [warn] quiz generation failed: {e}", file=sys.stderr)
        return None


_TOPIC_DISPLAY = {
    "dsa": "DSA",
    "ml-ai": "ML",
    "system-design": "System Design",
    "fullstack": "Fullstack",
}


def _format_topics(topics: list[str] | None) -> str:
    """Dedupe topics and join as 'A', 'A and B', or 'A, B, and C'."""
    display: list[str] = []
    for t in topics or []:
        name = _TOPIC_DISPLAY.get(t, t.title())
        if name not in display:
            display.append(name)
    if len(display) > 2:
        return ", ".join(display[:-1]) + ", and " + display[-1]
    if len(display) == 2:
        return f"{display[0]} and {display[1]}"
    return display[0] if display else ""


def _make_subject(mode: str, topics: list[str] | None = None,
                  has_quiz: bool = True) -> str:
    t_str = _format_topics(topics)

    if mode == "daily":
        suffix = " — Learn & Quiz" if has_quiz else ""
        if t_str:
            return f"📚 Scholar-Loop: {t_str}{suffix}"
        return f"📚 Scholar-Loop{suffix}"

    if mode == "quiz":
        if t_str:
            return f"🧩 Scholar-Loop Quiz: Testing your knowledge on {t_str}"
        return "🧩 Scholar-Loop Quiz"

    if t_str:
        return f"📝 Scholar-Loop: Today's focus is on {t_str}"
    return "📝 Scholar-Loop"


def compute_topic_slots(weights: dict, total_slots: int,
                        count_fn: Callable[[str], int]) -> dict[str, int]:
    topic_slots: dict[str, int] = {}
    for topic, weight in sorted(weights.items(), key=lambda x: -x[1]):
        available = count_fn(topic)
        if available == 0:
            continue
        slots = max(1, round(total_slots * weight))
        slots = min(slots, available)
        topic_slots[topic] = slots

    filled = sum(topic_slots.values())
    if filled < total_slots:
        for topic in weights:
            if topic in topic_slots:
                available = count_fn(topic)
                extra = min(total_slots - filled, available - topic_slots[topic])
                if extra > 0:
                    topic_slots[topic] += extra
                    filled += extra
                    if filled >= total_slots:
                        break
    return topic_slots


# ---------------------------------------------------------------------------
# Run modes
# ---------------------------------------------------------------------------

def _log_pick(mode: str, items: list[dict]) -> None:
    print(f"[{mode}] selected {len(items)} note(s):")
    for i, p in enumerate(items, 1):
        seq = p.get("sequence")
        seq_s = f" seq={seq}" if seq is not None else ""
        due = p.get("due") or "null"
        stab = p.get("stability")
        stab_s = f"{stab:.2f}" if isinstance(stab, (int, float)) else str(stab)
        print(
            f"  {i}. [{p.get('topic')}] {p.get('title')}"
            f"  path={p.get('path')}  due={due}  S={stab_s}"
            f"  rc={p.get('review_count', 0)}{seq_s}"
        )


def _select_learn_notes(conn: sqlite3.Connection, now: datetime,
                        dry_run: bool = False) -> list[dict]:
    """Pick today's Learn notes: proportional topic slots, ~1500-word cap, min 2 notes."""
    picked: list[dict] = []
    seen_ids: set = set()

    topic_slots = compute_topic_slots(
        TOPIC_WEIGHTS, NOTES_PER_LEARN,
        lambda t: count_due(conn, t, now)
    )
    if dry_run:
        print(f"[learn] topic slots: {topic_slots}")

    total_words = 0
    MAX_WORDS = 1500

    for topic, slots in topic_slots.items():
        if len(picked) >= MAX_NOTES_TOTAL:
            break
        allowed = min(slots, MAX_NOTES_TOTAL - len(picked))
        rows = pick_due_notes(conn, topic, allowed, exclude_ids=seen_ids, now=now)
        for r in rows:
            words = r["word_count"] or 0
            if len(picked) >= 2 and total_words + words > MAX_WORDS:
                # Skip this note if we already have 2 notes and it makes the email too long
                continue

            seen_ids.add(r["id"])
            path = r["path"]
            raw = read_note_content(path)
            if not raw:
                continue
            title = extract_title(raw) or r["title"]
            content_no_h1 = strip_h1(raw)
            content_html = render_markdown(content_no_h1)
            section_html = format_note_section(r, content_html)

            total_words += words
            picked.append({
                "id": r["id"],
                "path": path,
                "title": title,
                "topic": topic,
                "html": section_html,
                "due": r["due"],
                "stability": r["stability"],
                "review_count": r["review_count"],
                "sequence": r["sequence"] if "sequence" in r.keys() else None,
            })
    return picked


def _row_preview(r: sqlite3.Row) -> dict:
    return {
        "path": r["path"],
        "title": r["title"],
        "topic": r["topic"],
        "due": r["due"],
        "stability": r["stability"],
        "review_count": r["review_count"],
        "sequence": r["sequence"] if "sequence" in r.keys() else None,
    }


def _deliver(subject: str, html: str, send_fn: Callable | None) -> None:
    if send_fn:
        send_fn(subject, html, send_at=None)
    else:
        _send_email(subject, html, send_at=None)


def run_learn(dry_run: bool, now: datetime | None = None,
              send_fn: Callable | None = None) -> bool:
    if now is None:
        now = datetime.now(timezone.utc)
    today_str = now.strftime("%A, %d %b %Y")
    conn = get_db()

    picked = _select_learn_notes(conn, now, dry_run)
    if not picked:
        print("[learn] no due notes")
        conn.close()
        return False

    _log_pick("learn", picked)

    if dry_run:
        conn.close()
        return True

    sections_html = "".join(p["html"] for p in picked)
    full_html = HEADER_HTML.format(date=today_str, body=sections_html)
    subject = _make_subject("learn", [p["topic"] for p in picked])

    _deliver(subject, full_html, send_fn)

    for p in picked:
        mark_sent(conn, p["id"], now)

    conn.close()
    return True


def _select_quiz_rows(conn: sqlite3.Connection, limit: int,
                      exclude_ids: set | None = None) -> list[sqlite3.Row]:
    """Pick quiz notes from what you've already studied.

    Order: least recently quizzed first (never-quizzed first), then weakest memory
    (lowest FSRS stability), then oldest send. One note per topic before any topic
    repeats. Notes in `exclude_ids` (e.g. today's Learn notes) are skipped.
    Falls back to any note if nothing has been sent yet.
    """
    exclude_ids = exclude_ids or set()
    candidates = conn.execute(
        f"""SELECT {NOTE_SELECT_COLS}
           FROM notes
           WHERE last_sent IS NOT NULL
           ORDER BY last_quizzed ASC NULLS FIRST,
                    stability ASC NULLS LAST,
                    last_sent ASC"""
    ).fetchall()
    if not candidates:
        candidates = conn.execute(
            f"SELECT {NOTE_SELECT_COLS} FROM notes ORDER BY RANDOM()"
        ).fetchall()

    candidates = [r for r in candidates if r["id"] not in exclude_ids]

    picked: list[sqlite3.Row] = []
    picked_ids: set = set()
    seen_topics: set = set()
    for r in candidates:
        if len(picked) >= limit:
            break
        if r["topic"] not in seen_topics:
            picked.append(r)
            picked_ids.add(r["id"])
            seen_topics.add(r["topic"])
    for r in candidates:
        if len(picked) >= limit:
            break
        if r["id"] not in picked_ids:
            picked.append(r)
            picked_ids.add(r["id"])
    return picked


def mark_quizzed(conn: sqlite3.Connection, note_ids: list[int], now: datetime) -> None:
    """Record quiz rotation only. Does NOT touch FSRS scheduling state."""
    if not note_ids:
        return
    conn.executemany(
        "UPDATE notes SET last_quizzed=? WHERE id=?",
        [(now.isoformat(), i) for i in note_ids],
    )
    conn.commit()


def _build_quiz(rows: list[sqlite3.Row]) -> tuple[list[str], list[str], list[str], list[int]]:
    """Generate quiz sections. Returns (question sections, answer sections, topics, note ids)."""
    quiz_sections: list[str] = []
    answers_sections: list[str] = []
    delivered_topics: list[str] = []
    delivered_ids: list[int] = []

    for r in rows:
        raw = read_note_content(r["path"])
        if not raw:
            continue
        title = extract_title(raw) or r["title"]
        result = generate_quiz_qas(raw, title, r["topic"])
        if not result:
            continue

        q_html, a_html = result
        delivered_topics.append(r["topic"])
        delivered_ids.append(r["id"])

        quiz_sections.append(f"""<div class="note-section">
  <div class="meta-row">
    <span class="tag-topic">{r["topic"]}</span>
    <span class="tag-diff">{r["difficulty"] or "medium"}</span>
  </div>
  <h2>&#x1F9E9; {title}</h2>
  {q_html}
</div>""")

        answers_sections.append(f"""<div style="margin-bottom:20px;">
    <h3 style="margin-top:0; color:#4f46e5; font-size:16px;">{title}</h3>
    {a_html}
</div>""")

    return quiz_sections, answers_sections, delivered_topics, delivered_ids


def _answers_footer(answers_sections: list[str]) -> str:
    return f"""
    <div style="margin-top:40px; padding-top:40px; border-top:2px dashed #cbd5e1;">
      <h2 style="text-align:center; color:#64748b; font-size:20px; margin-bottom:30px;">Answers</h2>
      {"".join(answers_sections)}
    </div>
    """


def run_quiz(dry_run: bool, now: datetime | None = None,
             send_fn: Callable | None = None) -> bool:
    if now is None:
        now = datetime.now(timezone.utc)
    today_str = now.strftime("%A, %d %b %Y")
    conn = get_db()

    rows = _select_quiz_rows(conn, NOTES_PER_QUIZ)
    if not rows:
        print("[quiz] no notes available")
        conn.close()
        return False

    _log_pick("quiz", [_row_preview(r) for r in rows])

    if dry_run:
        conn.close()
        return True

    quiz_sections, answers_sections, delivered_topics, delivered_ids = _build_quiz(rows)

    if not quiz_sections:
        print("[quiz] quiz generation produced no sections (is GEMINI_API_KEY set?)")
        conn.close()
        return False

    body_html = "\n".join(quiz_sections) + _answers_footer(answers_sections)
    full_html = HEADER_HTML.format(date=today_str, body=body_html)
    subject = _make_subject("quiz", delivered_topics)

    _deliver(subject, full_html, send_fn)
    mark_quizzed(conn, delivered_ids, now)

    conn.close()
    return True


def run_daily(dry_run: bool, now: datetime | None = None,
              send_fn: Callable | None = None,
              preview_path: str | None = None) -> bool:
    """One combined email: Learn notes, then a short quiz, then answers at the bottom.

    If quiz generation fails, the Learn notes are still sent with a notice, and a
    GitHub Actions warning is raised so the failure is visible.
    `preview_path` builds the full email (including the LLM quiz) and writes it to a
    file without sending or changing the database.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    today_str = now.strftime("%A, %d %b %Y")
    conn = get_db()

    learn = _select_learn_notes(conn, now, dry_run)
    if learn:
        _log_pick("learn", learn)
    else:
        print("[daily] no due Learn notes today")

    quiz_rows = _select_quiz_rows(
        conn, NOTES_PER_DAILY_QUIZ, exclude_ids={p["id"] for p in learn}
    )
    if quiz_rows:
        _log_pick("quiz", [_row_preview(r) for r in quiz_rows])

    if dry_run and not preview_path:
        conn.close()
        return bool(learn or quiz_rows)

    quiz_sections, answers_sections, quiz_topics, quiz_ids = (
        _build_quiz(quiz_rows) if quiz_rows else ([], [], [], [])
    )
    quiz_failed = bool(quiz_rows) and not quiz_sections
    if quiz_failed:
        print("::warning title=Scholar-Loop quiz unavailable::Gemini quiz generation "
              "failed, so only the Learn notes were sent. Check GEMINI_API_KEY and the log.")

    if not learn and not quiz_sections:
        print("[daily] nothing to send")
        conn.close()
        return False

    parts: list[str] = []
    part_no = 1
    if learn:
        parts.append(
            f'<div class="part-heading">&#x1F4DA; Part {part_no} &middot; Today\'s notes</div>'
            + "".join(p["html"] for p in learn)
        )
        part_no += 1
    if quiz_sections:
        parts.append(
            '<div class="quiz-part">'
            f'<div class="part-heading">&#x1F9E9; Part {part_no} &middot; Active recall</div>'
            '<p class="part-intro">From notes you studied earlier. Answer in your head first; '
            'the answers are at the bottom.</p>'
            + "\n".join(quiz_sections)
            + "</div>"
        )
    elif quiz_failed:
        parts.append(
            '<div class="quiz-part">'
            '<div class="part-heading">&#x1F9E9; Active recall</div>'
            '<div class="notice">Quiz unavailable today: question generation failed. '
            'Your notes above are unaffected.</div></div>'
        )

    body_html = "\n".join(parts)
    if answers_sections:
        body_html += _answers_footer(answers_sections)

    full_html = HEADER_HTML.format(date=today_str, body=body_html)
    subject_topics = [p["topic"] for p in learn] if learn else quiz_topics
    subject = _make_subject("daily", subject_topics, has_quiz=bool(quiz_sections))

    if preview_path:
        html = transform(full_html)
        Path(preview_path).write_text(html, encoding="utf-8")
        size_kb = len(html.encode("utf-8")) / 1024
        print(f"[daily] subject: {subject}")
        print(f"[daily] preview written to {preview_path} "
              f"({size_kb:.1f} KB; Gmail clips at {GMAIL_CLIP_BYTES / 1024:.0f} KB)")
        conn.close()
        return True

    _deliver(subject, full_html, send_fn)

    for p in learn:
        mark_sent(conn, p["id"], now)
    mark_quizzed(conn, quiz_ids, now)

    conn.close()
    return True


# ---------------------------------------------------------------------------
# Send via Resend
# ---------------------------------------------------------------------------

def _send_email(subject: str, html: str, send_at: str | None):
    import httpx
    html = transform(html)

    size = len(html.encode("utf-8"))
    if size > GMAIL_CLIP_BYTES:
        print(f"::warning title=Scholar-Loop email may be clipped::HTML is {size / 1024:.0f} KB; "
              f"Gmail clips past {GMAIL_CLIP_BYTES / 1024:.0f} KB.")

    if not RESEND_API_KEY or not RECIPIENT:
        print("error: RESEND_API_KEY and RECIPIENT must be set", file=sys.stderr)
        sys.exit(1)

    payload = {
        "from": "Scholar-Loop <onboarding@resend.dev>",
        "to": [RECIPIENT],
        "subject": subject,
        "html": html,
    }
    if send_at:
        payload["scheduled_at"] = send_at

    resp = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    if resp.status_code >= 400:
        print(f"error sending: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Send the Scholar-Loop email")
    parser.add_argument("--mode", choices=["daily", "learn", "quiz"], default="daily",
                        help="daily = combined Learn + Quiz (default); learn or quiz alone")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show which notes would be picked, without sending")
    parser.add_argument("--preview", metavar="FILE",
                        help="daily mode: build the full email (calls Gemini) and write "
                             "the HTML to FILE without sending or changing the database")
    args = parser.parse_args()

    print(f"mode={args.mode} dry_run={args.dry_run} preview={args.preview}")
    if args.mode == "daily":
        ok = run_daily(args.dry_run or bool(args.preview), preview_path=args.preview)
    elif args.mode == "learn":
        ok = run_learn(args.dry_run)
    else:
        ok = run_quiz(args.dry_run)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
