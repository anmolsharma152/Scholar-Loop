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
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:40px 20px;background-color:#f3f4f6;">
<div style="max-width:850px;margin:0 auto;">
  <!-- Header -->
  <div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 16px 16px 0 0; padding: 40px; text-align: center;">
    <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.025em;">Scholar-Loop</h1>
    <p style="color: #c4b5fd; margin: 8px 0 0 0; font-size: 16px; font-weight: 500;">{date}</p>
  </div>
  
  <!-- Body -->
  <div style="background-color: #ffffff; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
    {notes}
  </div>

  <!-- Footer -->
  <div style="text-align:center; padding-top:30px;">
    <p style="font-size:14px; color:#6b7280; font-weight:500;">Daily learning, built on spaced repetition.</p>
  </div>
</div>
</body>
</html>"""

# Inner section — one per note
NOTE_SECTION = """
<div style="margin-bottom: 40px; padding-bottom: 40px; border-bottom: 1px solid #e5e7eb;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
    <span style="font-size:12px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;color:#4f46e5;background:#e0e7ff;padding:4px 10px;border-radius:6px;">{topic}</span>
    <span style="font-size:12px;font-weight:600;text-transform:uppercase;color:#6b7280;background:#f3f4f6;padding:4px 10px;border-radius:6px;">{difficulty}</span>
    {ai_badge}
  </div>
  <h2 style="margin:0 0 20px 0;font-size:28px;font-weight:800;color:#111827;line-height:1.2;">{title}</h2>
  <div style="color:#374151;font-size:16px;line-height:1.7;">
    {body}
  </div>
</div>
"""

AI_BADGE = '<span style="font-size:12px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;color:#ffffff;background:linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);padding:4px 10px;border-radius:6px;box-shadow:0 2px 4px rgba(236,72,153,0.3);">AI ENHANCED</span>'

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
Put all 3 answers inside a single HTML block styled like this so they are hidden until highlighted:
<blockquote style="color:#fff;background-color:#fff;border:1px solid #e5e7eb;padding:10px;border-radius:4px;">
<em>(Highlight to reveal answers)</em><br>
1. ...
</blockquote>

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


def apply_sequence_filters(pool: list[tuple[Path, frontmatter.Post]]) -> list[tuple[Path, frontmatter.Post]]:
    """
    For topics with a `sequence` field, ensure we only introduce the lowest sequence number
    that hasn't been read yet. Exclude all higher sequence numbers for unread notes.
    """
    topic_min_seqs = {}
    
    # 1. Find the lowest unread sequence number for each topic
    for path, post in pool:
        if score_note(post) == 1000.0:
            seq = post.metadata.get("sequence")
            if isinstance(seq, int):
                topic = post.metadata.get("topic", "unknown")
                if topic not in topic_min_seqs or seq < topic_min_seqs[topic]:
                    topic_min_seqs[topic] = seq
                    
    # 2. Filter the pool
    filtered = []
    for path, post in pool:
        seq = post.metadata.get("sequence")
        topic = post.metadata.get("topic", "unknown")
        
        # If it's an unread note with a sequence, check if it's the lowest available
        if score_note(post) == 1000.0 and isinstance(seq, int):
            if seq > topic_min_seqs.get(topic, -1):
                continue  # Skip this note, it's too advanced for now
                
        filtered.append((path, post))
        
    return filtered


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


def render_note_section(post: frontmatter.Post, path: Path, title: str, content: str, enhanced: bool) -> str:
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
        title=title,
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
        topic_pool = apply_sequence_filters(topic_pool)
        picked = pick_one(topic_pool)
        picks = [picked] if picked else []
    else:
        # Pick 2 notes from different topics
        picks = []
        chosen_topics = set()

        for _ in range(2):
            pool = [(p, post) for p, post in loaded if post.metadata.get("topic") not in chosen_topics]
            pool = apply_sequence_filters(pool)
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
        section = render_note_section(post, path, title=title, content=content, enhanced=enhanced)
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
