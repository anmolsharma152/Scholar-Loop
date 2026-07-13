#!/usr/bin/env python3
"""Daily email engine: picks 2 notes from knowledge/ via weighted random selection,
optionally enhances them with Groq (recap + quiz), renders into HTML, sends via Resend,
and commits updated metadata back to the repo.

Usage:
  python agent/send_daily.py                     # normal run
  python agent/send_daily.py --dry-run           # print without sending
  python agent/send_daily.py --topic dsa         # force-topic (single note)
"""

import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import markdown
from openai import OpenAI

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
TOPIC_DIRS = ["dsa", "system-design", "ml-ai", "fullstack", "papers", "agentic-ai", "sql"]
SKIP_FILES = {"README.md"}
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RECIPIENT = os.environ.get("RECIPIENT")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Outer wrapper — one per email
EMAIL_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:660px;margin:0 auto;padding:20px 16px;color:#1a1a1a;background:#f5f5f5;">
<p style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:#9ca3af;margin-bottom:20px;">Scholar-Loop &mdash; {date}</p>
{notes}
<p style="text-align:center;font-size:12px;color:#9ca3af;margin-top:28px;">Daily learning, built on spaced repetition.</p>
</body>
</html>"""

# Inner section — one per note
NOTE_SECTION = """
<div style="background:#fff;border-radius:12px;padding:28px 28px 20px;box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:20px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
    <span style="font-size:11px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#6b7280;">{topic}</span>
    <span style="font-size:11px;color:#d1d5db;">·</span>
    <span style="font-size:11px;color:#6b7280;">{difficulty}</span>
    {ai_badge}
  </div>
  {body}
</div>
"""

AI_BADGE = '<span style="font-size:10px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;color:#7c3aed;background:#f3f0ff;padding:2px 6px;border-radius:4px;">AI enhanced</span>'

GROQ_ENHANCE_SYSTEM = """You are an expert tutor creating a daily spaced-repetition email. 
Your goal is to synthesize the provided study note into a highly engaging, fast 2-minute read.

Structure your response exactly like this (use markdown):

### 🧠 The Core Intuition
Explain the main concept in 2-3 sentences as if explaining it to a smart peer. Use simple, clear language.

### 🔑 Key Takeaways
- Extract 3-5 of the most crucial points, insights, or architectures from the note.
- Keep bullet points punchy and memorable.
- Synthesize the knowledge; do NOT just copy-paste the original text.

### 🎯 Self-Test
Create 3 challenging questions based *only* on the note's content to test recall. 
Put all 3 answers inside a single markdown <details><summary>View Answers</summary> ... </details> block.

Do NOT output the original note content. Your response should be a complete, self-contained replacement that stands on its own."""


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_note(post) -> float:
    ls = post.metadata.get("last_sent")
    rc = post.metadata.get("review_count") or 0
    if not ls:
        return 1000.0
    delta = (datetime.now(timezone.utc) - ls).days
    s = delta * 10 - rc * 5
    return max(s, 1.0)


def find_notes(root: Path) -> list[tuple[Path, dict]]:
    notes = []
    for md in sorted(root.rglob("*.md")):
        if md.name in SKIP_FILES:
            continue
        notes.append(md)
    return notes


def load_notes(notes: list[Path]) -> list[tuple[Path, frontmatter.Post]]:
    loaded = []
    for path in notes:
        post = frontmatter.load(str(path))
        loaded.append((path, post))
    return loaded


def pick_one(pool: list[tuple[Path, frontmatter.Post]]) -> tuple[Path, frontmatter.Post] | None:
    if not pool:
        return None
    weights = [score_note(post) for _, post in pool]
    return random.choices(pool, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# LLM enhancement
# ---------------------------------------------------------------------------

def enhance_with_llm(content: str, title: str, topic: str) -> str | None:
    if not GROQ_API_KEY:
        return None
    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
        )
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": GROQ_ENHANCE_SYSTEM},
                {"role": "user", "content": f"# {title}\n\nTopic: {topic}\n\n{content}"},
            ],
            temperature=0.5,
            max_tokens=2048,
        )
        enhanced = resp.choices[0].message.content.strip()
        if len(enhanced) < 100:
            return None
        return enhanced
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def extract_title(content: str, path: Path) -> str:
    """Extract title from the first # H1 heading in content, falling back to filename slug."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def render_note_section(post: frontmatter.Post, path: Path, content: str, enhanced: bool) -> str:
    """Render a single note as an HTML section (not a full document)."""
    meta = post.metadata
    topic = meta.get("topic", "unknown")
    difficulty = meta.get("difficulty", "unknown")
    ai_badge = AI_BADGE if enhanced else ""
    body_html = markdown.markdown(
        content,
        extensions=["fenced_code", "tables", "nl2br", "sane_lists", "md_in_html"],
    )
    return NOTE_SECTION.format(
        topic=topic,
        difficulty=difficulty,
        ai_badge=ai_badge,
        body=body_html,
    )


# ---------------------------------------------------------------------------
# Sending
# ---------------------------------------------------------------------------

def send_via_resend(subject: str, html: str):
    import httpx

    if not RESEND_API_KEY or not RECIPIENT:
        print("error: RESEND_API_KEY and RECIPIENT must be set", file=sys.stderr)
        sys.exit(1)

    resp = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Scholar-Loop <onboarding@resend.dev>",
            "to": [RECIPIENT],
            "subject": subject,
            "html": html,
        },
        timeout=30,
    )
    if resp.status_code >= 400:
        print(f"error sending: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)
    print(f"email sent: {subject}")


# ---------------------------------------------------------------------------
# Metadata update
# ---------------------------------------------------------------------------

def update_meta(path: Path, post: frontmatter.Post):
    post["last_sent"] = datetime.now(timezone.utc)
    post["review_count"] = (post.metadata.get("review_count") or 0) + 1
    with open(path, "w") as f:
        f.write(frontmatter.dumps(post))
    print(f"metadata updated: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Send daily Scholar-Loop email")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--topic", help="Force-select a specific topic (single note)")
    args = parser.parse_args()

    # Collect all notes
    all_notes = []
    for topic in TOPIC_DIRS:
        dir_path = KNOWLEDGE_DIR / topic
        if dir_path.exists():
            all_notes.extend(find_notes(dir_path))
        else:
            print(f"warning: directory not found: {dir_path}")

    if not all_notes:
        print("no notes found", file=sys.stderr)
        sys.exit(0)

    loaded = load_notes(all_notes)

    if args.topic:
        topic_pool = [(p, post) for p, post in loaded if post.metadata.get("topic") == args.topic]
        if not topic_pool:
            print(f"no notes for topic: {args.topic}", file=sys.stderr)
            sys.exit(1)
        picks = [(pick_one(topic_pool), False)]
    else:
        # Pick 2 notes from different topics
        picks = []
        chosen_topics = set()

        for _ in range(2):
            pool = [(p, post) for p, post in loaded if post.metadata.get("topic") not in chosen_topics]
            picked = pick_one(pool)
            if picked:
                chosen_topics.add(picked[1].metadata.get("topic"))
                picks.append(picked)

        if not picks:
            print("could not pick any notes", file=sys.stderr)
            sys.exit(1)

    # Process each pick
    note_sections = []
    pick_labels = []

    for path, post in picks:
        content = post.content
        title = extract_title(content, path)
        topic = post.metadata.get("topic", "unknown")

        if args.dry_run:
            print(f"[DRY RUN] topic={topic} title={title} path={path}")
            enhanced = False
        else:
            enhanced_content = enhance_with_llm(content, title, topic)
            if enhanced_content:
                content = enhanced_content   # use enhanced text in render
                enhanced = True
                print(f"  enhanced: {path.name}")
            else:
                enhanced = False

        pick_labels.append(title)

        if args.dry_run:
            print(f"  score={score_note(post):.1f}")
            continue

        update_meta(path, post)
        section = render_note_section(post, path, content=content, enhanced=enhanced)
        note_sections.append(section)

    if args.dry_run:
        print("\n[dry run complete — no email sent]")
        return

    if not note_sections:
        print("nothing to send", file=sys.stderr)
        sys.exit(0)

    subject = f"Scholar-Loop: {', '.join(pick_labels[:2])}"
    date_str = datetime.now(timezone.utc).strftime("%A, %d %b %Y")
    combined_html = EMAIL_WRAPPER.format(
        subject=subject,
        date=date_str,
        notes="\n".join(note_sections),
    )

    send_via_resend(subject, combined_html)
    print("done")


if __name__ == "__main__":
    main()
