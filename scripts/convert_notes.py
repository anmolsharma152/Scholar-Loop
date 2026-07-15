#!/usr/bin/env python3
"""Convert PDFs and DOCX files into markdown study notes with frontmatter.

Usage:
    python scripts/convert_notes.py ~/Downloads/*.pdf
    python scripts/convert_notes.py --source ~/Downloads --topic papers
    python scripts/convert_notes.py --dry-run ~/Downloads/*.pdf
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import pdfplumber
from docx import Document
from openai import OpenAI

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

TOPIC_KEYWORDS = {
    "dsa": ["algorithm", "data structure", "tree", "graph", "sort", "search", "dynamic programming", "greedy", "stack", "queue", "hash", "linked list", "array", "recursion", "backtracking", "binary", "heap", "trie", "bfs", "dfs"],
    "system-design": ["system design", "scalability", "distributed", "load balancer", "caching", "cdn", "microservice", "api gateway", "database design", "high availability", "consistent hashing", "message queue"],
    "ml-ai": ["machine learning", "deep learning", "neural network", "transformer", "attention", "cnn", "rnn", "lstm", "gan", "reinforcement learning", "nlp", "computer vision", "optimization", "gradient", "loss function", "overfitting", "regularization", "classification", "regression", "clustering"],
    "fullstack": ["react", "fastapi", "django", "flask", "typescript", "javascript", "python", "async", "database", "sql", "rest api", "graphql", "html", "css", "node", "docker", "kubernetes", "ci/cd", "testing"],
    "papers": ["paper", "research", "arxiv", "abstract", "methodology", "experiment", "benchmark", "state of the art", "sota", "novel approach"],
    "agentic-ai": ["agent", "agentic", "llm", "prompt engineering", "rag", "retrieval augmented", "tool use", "function calling", "multi-agent", "chain of thought", "reasoning"],
    "sql": ["sql", "query", "join", "index", "transaction", "normalization", "aggregation", "subquery", "window function", "stored procedure", "view", "trigger", "postgresql", "mysql", "database"],
}

CONVERSION_PROMPT = """Convert this document into a concise study note (400-600 words).

Output format: YAML frontmatter + markdown body.

Frontmatter fields (exact names):
- title: clear, descriptive title
- topic: one of [dsa, system-design, ml-ai, fullstack, papers, agentic-ai, sql]
- difficulty: one of [easy, medium, hard]
- tags: list of 2-4 relevant tags
- created: today's date in ISO format

Body structure:
- Start with an H1 heading (# Title)
- 2-3 paragraphs explaining the core concept
- Key formulas or code snippets if relevant (use markdown code blocks)
- 3-5 key takeaways as bullet points
- Keep total length 400-600 words

Rules:
- Synthesize, don't just copy-paste. Write as if creating a study card.
- If the source has images, describe what they show in text.
- If the source covers multiple topics, focus on the primary one.
- Use clear, concise language. No fluff.

Output ONLY the frontmatter + markdown. No commentary."""


def extract_text_pdf(path: Path) -> str:
    text_parts = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
    except Exception as e:
        print(f"  error reading PDF {path.name}: {e}", file=sys.stderr)
        return ""
    return "\n\n".join(text_parts)


def extract_text_docx(path: Path) -> str:
    try:
        doc = Document(str(path))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"  error reading DOCX {path.name}: {e}", file=sys.stderr)
        return ""


def classify_topic(text: str, filename: str) -> str:
    combined = (filename + " " + text[:2000]).lower()
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        scores[topic] = sum(1 for kw in keywords if kw in combined)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "papers"


def convert_to_note(text: str, filename: str, topic_override: str | None = None) -> tuple[frontmatter.Post, str] | None:
    if not GROQ_API_KEY:
        print("error: GROQ_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if topic_override:
        topic_hint = f"Force topic to: {topic_override}"
    else:
        topic_hint = "Classify topic automatically from the list above."

    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

    # Truncate to ~8000 tokens to stay within context
    truncated = text[:24000]

    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": CONVERSION_PROMPT},
                {"role": "user", "content": f"Source file: {filename}\n{topic_hint}\n\n{truncated}"},
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        output = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  LLM error: {e}", file=sys.stderr)
        return None

    # Parse frontmatter from LLM output
    auto_topic = topic_override or classify_topic(text, filename)
    fallback_title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    if output.startswith("---"):
        try:
            post = frontmatter.loads(output)
            # Fill missing fields
            if not post.metadata.get("title"):
                post["title"] = fallback_title
            if topic_override:
                post["topic"] = topic_override
            elif not post.metadata.get("topic") or post.metadata["topic"] not in TOPIC_KEYWORDS:
                post["topic"] = auto_topic
            if not post.metadata.get("difficulty"):
                post["difficulty"] = "medium"
            if not post.metadata.get("created"):
                post["created"] = datetime.now(timezone.utc).date().isoformat()
            if not post.metadata.get("tags"):
                post["tags"] = []
            return post, frontmatter.dumps(post)
        except Exception:
            pass

    # If LLM didn't produce valid frontmatter, wrap it
    post = frontmatter.Post(
        output,
        title=fallback_title,
        topic=auto_topic,
        difficulty="medium",
        tags=[],
        created=datetime.now(timezone.utc).date().isoformat(),
    )
    return post, frontmatter.dumps(post)


def slugify(title: str) -> str:
    import re
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)  # remove non-word chars
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    return slug


def process_file(path: Path, topic_override: str | None, dry_run: bool) -> bool:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = extract_text_pdf(path)
    elif suffix == ".docx":
        text = extract_text_docx(path)
    else:
        print(f"  skip unsupported format: {path.name}")
        return False

    if not text.strip() or len(text) < 100:
        print(f"  skip empty/too short: {path.name}")
        return False

    print(f"  extracted {len(text)} chars from {path.name}")

    result = convert_to_note(text, path.name, topic_override)
    if not result:
        return False

    post, raw_output = result
    topic = post.metadata.get("topic", "papers")
    slug = slugify(post.metadata.get("title", path.stem))
    out_dir = KNOWLEDGE_DIR / topic
    out_path = out_dir / f"{slug}.md"

    if dry_run:
        print(f"  [DRY RUN] would write: {out_path}")
        print(f"  title: {post.metadata.get('title')}")
        print(f"  topic: {topic}")
        word_count = len(post.content.split())
        print(f"  words: {word_count}")
        return True

    out_dir.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        print(f"  skip existing: {out_path.relative_to(KNOWLEDGE_DIR.parent)}")
        return False

    with open(out_path, "w") as f:
        f.write(raw_output)

    print(f"  wrote: {out_path.relative_to(KNOWLEDGE_DIR.parent)}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Convert PDFs/DOCX to study notes")
    parser.add_argument("files", nargs="*", help="Files to convert")
    parser.add_argument("--source", help="Directory to scan for files")
    parser.add_argument("--topic", help="Force all files into a specific topic")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    files = []
    if args.source:
        src = Path(args.source)
        files = sorted(src.glob("*.pdf")) + sorted(src.glob("*.docx"))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        parser.print_help()
        sys.exit(1)

    if not files:
        print("no files found")
        sys.exit(0)

    print(f"processing {len(files)} files...")
    converted = 0
    for f in files:
        if process_file(f, args.topic, args.dry_run):
            converted += 1

    print(f"\ndone: {converted}/{len(files)} converted")


if __name__ == "__main__":
    main()
