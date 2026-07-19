#!/usr/bin/env python3
"""Daily Scholar-Loop email: FSRS-driven note selection, Learn (morning) and Quiz (evening) modes.

Usage:
  python agent/send_daily.py                             # learn (morning)
  python agent/send_daily.py --mode quiz                 # quiz (evening)
  python agent/send_daily.py --dry-run                   # preview learn without sending
  python agent/send_daily.py --dry-run --mode quiz       # preview quiz without sending
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
from openai import OpenAI
from premailer import transform


KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "user.db"
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RECIPIENT = os.environ.get("RECIPIENT")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TOPIC_WEIGHTS = {
    "dsa": 0.28,
    "ml-ai": 0.22,
    "papers": 0.20,
    "system-design": 0.16,
    "fullstack": 0.14,
}

NOTES_PER_LEARN = 4
NOTES_PER_QUIZ = 4
MAX_NOTES_TOTAL = 5

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

TOPIC_DIRS = [
    "dsa", "system-design", "ml-ai", "fullstack", "papers",
]
SKIP_FILES = {"README.md"}

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
    if not GROQ_API_KEY:
        return None
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
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
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )
        result = resp.choices[0].message.content.strip()
        
        # Parse the Q1/A1 format
        questions_html = []
        answers_html = []
        
        lines = result.split("\n")
        q_count = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Q") and ". " in line[:5]:
                questions_html.append(f'<div class="quiz-q">{line}</div>')
            elif line.startswith("A") and ". " in line[:5]:
                # Style the answer block like a newsletter answer
                answer_text = line.split(". ", 1)[1] if ". " in line else line
                answers_html.append(f'<div class="quiz-answer"><strong>Q{q_count}:</strong> {answer_text}</div>')
                q_count += 1
                
        if not questions_html or not answers_html:
            return None
            
        return "\n".join(questions_html), "\n".join(answers_html)
    except Exception as e:
        print(f"  [warn] quiz gen failed: {e}", file=sys.stderr)
        return None


def _make_subject(mode: str, topics: list[str]) -> str:
    # Deduplicate and format topics nicely
    unique_topics = []
    for t in topics:
        if t not in unique_topics:
            unique_topics.append(t)
            
    # Map raw topic names to readable names if desired, e.g., 'ml-ai' -> 'ML/AI'
    display_topics = []
    for t in unique_topics:
        if t == "dsa": display_topics.append("DSA")
        elif t == "ml-ai": display_topics.append("ML")
        elif t == "system-design": display_topics.append("System Design")
        elif t == "fullstack": display_topics.append("Fullstack")
        else: display_topics.append(t.title())
        
    t_str = ""
    if len(display_topics) > 1:
        t_str = ", ".join(display_topics[:-1]) + ", and " + display_topics[-1]
    elif len(display_topics) == 1:
        t_str = display_topics[0]
        
    if mode == "quiz":
        if t_str:
            return f"🧩 Scholar-Loop Quiz: Testing your knowledge on {t_str}"
        return "🧩 Scholar-Loop Quiz"
    else:
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


def run_learn(dry_run: bool, now: datetime | None = None,
              send_fn: Callable | None = None) -> bool:
    if now is None:
        now = datetime.now(timezone.utc)
    today_str = now.strftime("%A, %d %b %Y")
    conn = get_db()
    picked = []
    seen_ids = set()

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
    
    topics_picked = [p["topic"] for p in picked]
    subject = _make_subject("learn", topics_picked)

    if send_fn:
        send_fn(subject, full_html, send_at=None)
    else:
        _send_email(subject, full_html, send_at=None)

    for p in picked:
        mark_sent(conn, p["id"], now)

    conn.close()
    return True


def run_quiz(dry_run: bool, now: datetime | None = None,
             send_fn: Callable | None = None) -> bool:
    if now is None:
        now = datetime.now(timezone.utc)
    today_str = now.strftime("%A, %d %b %Y")
    conn = get_db()

    rows = conn.execute(
        f"""SELECT {NOTE_SELECT_COLS}
           FROM notes
           WHERE last_sent IS NOT NULL
           ORDER BY ROW_NUMBER() OVER (PARTITION BY topic ORDER BY RANDOM()), RANDOM()
           LIMIT ?""",
        (NOTES_PER_QUIZ,)
    ).fetchall()

    if not rows:
        rows = conn.execute(
            f"""SELECT {NOTE_SELECT_COLS}
               FROM notes
               ORDER BY ROW_NUMBER() OVER (PARTITION BY topic ORDER BY RANDOM()), RANDOM()
               LIMIT ?""",
            (NOTES_PER_QUIZ,)
        ).fetchall()

    if not rows:
        print("[quiz] no notes available")
        conn.close()
        return False

    preview = [{
        "path": r["path"],
        "title": r["title"],
        "topic": r["topic"],
        "due": r["due"],
        "stability": r["stability"],
        "review_count": r["review_count"],
        "sequence": r["sequence"] if "sequence" in r.keys() else None,
    } for r in rows]
    _log_pick("quiz", preview)

    if dry_run:
        conn.close()
        return True

    quiz_sections = []
    answers_sections = []

    for r in rows:
        raw = read_note_content(r["path"])
        if not raw:
            continue
        title = extract_title(raw) or r["title"]
        result = generate_quiz_qas(raw, title, r["topic"])
        if not result:
            continue
        
        q_html, a_html = result

        section = f"""<div class="note-section">
  <div class="meta-row">
    <span class="tag-topic">{r["topic"]}</span>
    <span class="tag-diff">{r["difficulty"] or "medium"}</span>
  </div>
  <h2>&#x1F9E9; {title}</h2>
  {q_html}
</div>"""
        quiz_sections.append(section)
        
        # Add to answers footer
        answers_sections.append(f"""<div style="margin-bottom:20px;">
    <h3 style="margin-top:0; color:#4f46e5; font-size:16px;">{title}</h3>
    {a_html}
</div>""")

    if not quiz_sections:
        print("[quiz] quiz generation produced no sections (need GROQ_API_KEY?)")
        conn.close()
        return False

    # Build the main body with questions, and then append the answers at the bottom
    body_html = "\n".join(quiz_sections)
    
    # Answers Footer
    answers_footer = f"""
    <div style="margin-top:40px; padding-top:40px; border-top:2px dashed #cbd5e1;">
      <h2 style="text-align:center; color:#64748b; font-size:20px; margin-bottom:30px;">Answers</h2>
      {"".join(answers_sections)}
    </div>
    """
    
    body_html += answers_footer

    full_html = HEADER_HTML.format(date=today_str, body=body_html)
    
    topics_picked = [p["topic"] for p in preview]
    subject = _make_subject("quiz", topics_picked)

    if send_fn:
        send_fn(subject, full_html, send_at=None)
    else:
        _send_email(subject, full_html, send_at=None)

    conn.close()
    return True


# ---------------------------------------------------------------------------
# Send via Resend
# ---------------------------------------------------------------------------

def _send_email(subject: str, html: str, send_at: str | None):
    import httpx
    html = transform(html)

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

    parser = argparse.ArgumentParser(description="Send daily Scholar-Loop email")
    parser.add_argument("--mode", choices=["learn", "quiz", "both"], default="both",
                        help="learn (morning), quiz (evening), or both (default)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without sending")
    args = parser.parse_args()

    modes = ["learn", "quiz"] if args.mode == "both" else [args.mode]
    ok = True

    for mode in modes:
        print(f"mode={mode} dry_run={args.dry_run}")
        if mode == "learn":
            ok = run_learn(args.dry_run) and ok
        else:
            ok = run_quiz(args.dry_run) and ok

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
