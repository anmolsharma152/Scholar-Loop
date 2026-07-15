#!/usr/bin/env python3
"""Daily Scholar-Loop email: FSRS-driven note selection, Learn (morning) and Quiz (evening) modes.

Usage:
  python agent/send_daily.py                             # learn (morning)
  python agent/send_daily.py --mode quiz                 # quiz (evening)
  python agent/send_daily.py --dry-run                   # preview learn without sending
  python agent/send_daily.py --dry-run --mode quiz       # preview quiz without sending
"""

import json
import os
import random
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import frontmatter
import markdown
from fsrs import Scheduler, Card, Rating
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "user.db"
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RECIPIENT = os.environ.get("RECIPIENT")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%A, %d %b %Y")

# FSRS
SCHEDULER = Scheduler(desired_retention=0.8)

# Topic weights for proportional selection
TOPIC_WEIGHTS = {
    "dsa": 0.35,
    "system-design": 0.20,
    "sql": 0.10,
    "fullstack": 0.10,
    "ml-ai": 0.10,
    "papers": 0.08,
    "agentic-ai": 0.07,
}

NOTES_PER_LEARN = 4
NOTES_PER_QUIZ = 4
MAX_NOTES_TOTAL = 5  # Cap total notes across all topics per email

# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------

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
  .quiz-spoiler summary {{ cursor:pointer; color:#4f46e5; font-weight:600; font-size:14px; padding:4px 0; }}
  .quiz-spoiler {{ margin:0 0 20px; }}
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

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

TOPIC_DIRS = [
    "dsa", "system-design", "ml-ai", "fullstack", "papers",
    "agentic-ai", "sql"
]
SKIP_FILES = {"README.md"}


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def count_due(conn, topic: str) -> int:
    """Number of notes due for this topic."""
    return conn.execute(
        "SELECT COUNT(*) FROM notes WHERE topic=? AND (due IS NULL OR due <= ?)",
        (topic, NOW.isoformat())
    ).fetchone()[0]


def pick_due_notes(conn, topic: str, count: int, exclude_ids: set = None) -> list[sqlite3.Row]:
    """Pick `count` due notes from a topic, lowest retrievability first."""
    exclude_clause = ""
    params = [topic, NOW.isoformat()]
    if exclude_ids:
        placeholders = ",".join("?" for _ in exclude_ids)
        exclude_clause = f" AND id NOT IN ({placeholders})"
        params.extend(exclude_ids)

    rows = conn.execute(
        f"""SELECT id, path, title, topic, difficulty, tags, word_count,
                   stability, difficulty_fsrs, due, review_count, last_sent
            FROM notes
            WHERE topic=? AND (due IS NULL OR due <= ?)
            {exclude_clause}
            ORDER BY due ASC NULLS FIRST
            LIMIT ?""",
        (*params, count)
    ).fetchall()
    return rows


def compute_retrievability(stability: float, difficulty: float, last_sent: str | None) -> float:
    """FSRS retrievability at NOW. Returns 0.0 if never sent."""
    if not last_sent or stability <= 0:
        return 0.0
    try:
        last = datetime.fromisoformat(last_sent)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return 0.0
    elapsed = (NOW - last).days
    if elapsed < 0:
        elapsed = 0
    # Retrievability formula from FSRS
    R = (1 + 2.71828 ** ((elapsed * (1.1 - difficulty / 10)) / stability - 1.09 * difficulty + 7.37)) ** -1
    return max(R, 0.0)


def mark_sent(conn, note_id: int):
    now_iso = NOW.isoformat()
    conn.execute(
        """UPDATE notes SET last_sent=?, review_count=review_count+1, due=?
           WHERE id=?""",
        (now_iso, now_iso, note_id)
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Learn mode: pick notes, read .md, render
# ---------------------------------------------------------------------------

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
    """Remove the first # H1 heading — title is rendered separately."""
    lines = content.splitlines()
    # Find first non-empty line that starts with "# "
    for i, line in enumerate(lines):
        if line.strip().startswith("# "):
            # Remove it and any following blank lines
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
  <h2>{row["title"]}</h2>
  <div class="content">{content_html}</div>
</div>"""


def generate_quiz_qas(content: str, title: str, topic: str) -> str | None:
    """Use Groq to generate quiz Q&A from raw note content. Returns HTML string."""
    if not GROQ_API_KEY:
        return None
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
        prompt = f"""You are a quiz generator. Given the following study note, generate EXACTLY 3 quiz questions that test understanding of the key concepts.

Each question must follow this exact format:

Q1. [question text]
<details class="quiz-spoiler"><summary>Show answer</summary>
Answer: [concise answer]
</details>

Q2. [question text]
<details class="quiz-spoiler"><summary>Show answer</summary>
Answer: [concise answer]
</details>

Q3. [question text]
<details class="quiz-spoiler"><summary>Show answer</summary>
Answer: [concise answer]
</details>

Rules:
- Questions must be answerable from the note content alone.
- Answers must be factual, specific, and 1-3 sentences.
- Do NOT include the questions' answers anywhere else in the output.
- Output only the 3 Q&A blocks, nothing else.

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
        if len(result) < 50:
            return None
        return result
    except Exception as e:
        print(f"  [warn] quiz gen failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Learn (morning email)
# ---------------------------------------------------------------------------

def run_learn(dry_run: bool) -> bool:
    conn = get_db()
    picked = []
    seen_ids = set()

    # Proportional selection by topic weight
    total_slots = NOTES_PER_LEARN
    topic_slots = {}
    for topic, weight in sorted(TOPIC_WEIGHTS.items(), key=lambda x: -x[1]):
        available = count_due(conn, topic)
        if available == 0:
            continue
        slots = max(1, round(total_slots * weight))
        slots = min(slots, available)
        topic_slots[topic] = slots

    # Fill remaining slots in case rounding undershoots
    filled = sum(topic_slots.values())
    if filled < total_slots:
        for topic in TOPIC_WEIGHTS:
            if topic in topic_slots:
                available = count_due(conn, topic)
                extra = min(total_slots - filled, available - topic_slots[topic])
                if extra > 0:
                    topic_slots[topic] += extra
                    filled += extra
                    if filled >= total_slots:
                        break

    for topic, slots in topic_slots.items():
        if len(picked) >= MAX_NOTES_TOTAL:
            break
        allowed = min(slots, MAX_NOTES_TOTAL - len(picked))
        rows = pick_due_notes(conn, topic, allowed, exclude_ids=seen_ids)
        for r in rows:
            seen_ids.add(r["id"])
            path = r["path"]
            raw = read_note_content(path)
            if not raw:
                continue
            title = extract_title(raw) or r["title"]
            content_no_h1 = strip_h1(raw)
            content_html = render_markdown(content_no_h1)
            section_html = format_note_section(r, content_html)

            picked.append({
                "id": r["id"],
                "path": path,
                "title": title,
                "topic": topic,
                "html": section_html,
            })

    if not picked:
        print("no notes due for learn")
        conn.close()
        return False

    if dry_run:
        for p in picked:
            print(f"  [learn] {p['topic']:15s} {p['title']}")
        conn.close()
        return True

    # Send
    sections_html = "".join(p["html"] for p in picked)
    full_html = HEADER_HTML.format(date=TODAY, body=sections_html)
    subject = "Scholar-Loop: " + ", ".join(p["title"] for p in picked[:3])
    if len(picked) > 3:
        subject += f" +{len(picked) - 3} more"

    _send_email(subject, full_html, send_at=None)  # immediate

    # Mark sent
    for p in picked:
        mark_sent(conn, p["id"])

    conn.close()
    print(f"learn sent: {len(picked)} notes")
    return True


# ---------------------------------------------------------------------------
# Quiz (evening email)
# ---------------------------------------------------------------------------

def run_quiz(dry_run: bool) -> bool:
    conn = get_db()

    # Pick notes that were sent before today (ever reviewed)
    # Prioritize ones with lowest retrievability (due soon)
    rows = conn.execute(
        """SELECT id, path, title, topic, difficulty, stability, difficulty_fsrs, last_sent
           FROM notes
           WHERE last_sent IS NOT NULL
           ORDER BY last_sent ASC
           LIMIT ?""",
        (NOTES_PER_QUIZ,)
    ).fetchall()

    if not rows:
        # Fallback: any note (brand new, just quiz on something)
        rows = conn.execute(
            """SELECT id, path, title, topic, difficulty, stability, difficulty_fsrs, last_sent
               FROM notes
               ORDER BY RANDOM()
               LIMIT ?""",
            (NOTES_PER_QUIZ,)
        ).fetchall()

    if not rows:
        print("no notes available for quiz")
        conn.close()
        return False

    if dry_run:
        for r in rows:
            print(f"  [quiz]  {r['topic']:15s} {r['title']}")
        conn.close()
        return True

    quiz_sections = []

    for r in rows:
        raw = read_note_content(r["path"])
        if not raw:
            continue
        title = extract_title(raw) or r["title"]
        qa_html = generate_quiz_qas(raw, title, r["topic"])
        if not qa_html:
            continue

        section = f"""<div class="note-section">
  <div class="meta-row">
    <span class="tag-topic">{r["topic"]}</span>
    <span class="tag-diff">{r["difficulty"] or "medium"}</span>
  </div>
  <h2>🧩 {title}</h2>
  {qa_html}
</div>"""
        quiz_sections.append(section)

    if not quiz_sections:
        print("quiz generation produced no output")
        conn.close()
        return False

    body_html = "\n".join(quiz_sections)
    full_html = HEADER_HTML.format(date=TODAY, body=body_html)
    subject = "Scholar-Loop Quiz: " + ", ".join(r["title"] for r in rows[:3])
    if len(rows) > 3:
        subject += f" +{len(rows) - 3} more"

    # Schedule for 4 PM IST (10:30 UTC)
    evening = NOW.replace(hour=10, minute=30, second=0, microsecond=0)
    if evening <= NOW:
        evening += timedelta(days=1)
    send_at = evening.isoformat()

    _send_email(subject, full_html, send_at=send_at)
    conn.close()
    print(f"quiz sent: {len(quiz_sections)} notes, scheduled for {send_at}")
    return True


# ---------------------------------------------------------------------------
# Send via Resend
# ---------------------------------------------------------------------------

def _send_email(subject: str, html: str, send_at: str | None):
    import httpx

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
    print(f"email sent: {subject}" + (f" (scheduled {send_at})" if send_at else ""))


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
