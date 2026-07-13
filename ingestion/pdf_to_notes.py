#!/usr/bin/env python3
"""One-off backfill: ingest research PDFs → knowledge/papers/*.md.

Uses Gemini 2.5 Flash for native PDF understanding + structured extraction.
Outputs clean markdown notes with YAML frontmatter, ready for the email rotation.

Usage:
  python ingestion/pdf_to_notes.py                          # process all PDFs
  python ingestion/pdf_to_notes.py --dry-run                  # preview only
  python ingestion/pdf_to_notes.py --max 5                    # first 5 PDFs
  python ingestion/pdf_to_notes.py --skip-existing            # skip already-ingested
"""

import argparse
import logging
import os
import re
import sys
import time
from pathlib import Path

from google import genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pdf_to_notes")

PDF_DIR = Path.home() / "Anmol" / "Research Papers"
DEST_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "papers"
RATE_LIMIT_SLEEP = 2.0  # seconds between API calls

SYSTEM_PROMPT = """You are a research-paper summarizer. Given a PDF, produce a structured
markdown note with these sections:

1. A 3-5 sentence summary explaining the core contribution.
2. Key technical details (architecture, algorithm, training setup, etc.).
3. Results / benchmarks (numbers, comparisons).
4. Limitations and open questions.

Rules:
- Use clear headings (##).
- Keep each note under 500 words.
- Use LaTeX ($...$) for math notation.
- Be precise — state numbers, model sizes, dataset names when present.
- Do NOT add YAML frontmatter — the caller will prepend it.

Respond with the markdown body only (no extra commentary)."""

NOTE_TEMPLATE = """---
topic: papers
difficulty: medium
tags:
  - {tag}
last_sent:
review_count: 0
---

{body}
"""


def _pdf_title(filename: str) -> str:
    name = filename.replace(".pdf", "").strip()
    name = re.sub(r"[_-]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _infer_tag(filename: str) -> str:
    name = filename.lower()
    if any(w in name for w in ("transformer", "attention", "bert", "gpt", "llm", "language model")):
        return "llm"
    if any(w in name for w in ("diffusion", "vae", "gan", "generative")):
        return "generative"
    if any(w in name for w in ("vision", "cnn", "image", "convnet", "resnet")):
        return "computer-vision"
    if any(w in name for w in ("reinforcement", "rl", "decision")):
        return "reinforcement-learning"
    if any(w in name for w in ("graph", "gnn")):
        return "graph"
    return "deep-learning"


def extract_with_gemini(pdf_path: Path, api_key: str) -> str | None:
    client = genai.Client(api_key=api_key)

    pdf_file = client.files.upload(file=pdf_path)
    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=[pdf_file, "Summarize this paper into a structured markdown note."],
        config={"system_instruction": SYSTEM_PROMPT},
    )
    return response.text.strip() if response.text else None


def main():
    parser = argparse.ArgumentParser(description="Backfill PDFs into knowledge/papers/")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without processing")
    parser.add_argument("--max", type=int, default=None, help="Max PDFs to process")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if dest file exists")
    parser.add_argument("--api-key", help="Gemini API key (default: GEMINI_API_KEY env)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.error("GEMINI_API_KEY not set. Provide --api-key or set the env var.")
        sys.exit(1)

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        log.warning("No PDFs found in %s", PDF_DIR)
        sys.exit(0)

    if args.max:
        pdfs = pdfs[: args.max]

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    existing = {f.stem for f in DEST_DIR.glob("*.md")}
    skipped_count = 0
    success_count = 0
    error_count = 0

    for pdf in pdfs:
        title = _pdf_title(pdf.name)
        dest_stem = pdf.stem.lower().replace(" ", "-").replace("_", "-")
        dest_stem = re.sub(r"[^a-z0-9-]", "", dest_stem)
        dest_path = DEST_DIR / f"{dest_stem}.md"

        if args.skip_existing and dest_path.exists():
            log.info("  skip (exists): %s", pdf.name)
            skipped_count += 1
            continue

        if args.dry_run:
            log.info("  would process: %s → %s", pdf.name, dest_path.name)
            continue

        log.info("  processing: %s ...", pdf.name)
        try:
            body = extract_with_gemini(pdf, api_key)
            if not body:
                log.warning("  empty response for: %s", pdf.name)
                error_count += 1
                continue

            tag = _infer_tag(pdf.name)
            note = NOTE_TEMPLATE.format(tag=tag, body=body)
            dest_path.write_text(note)

            log.info("  wrote: %s  (tag=%s)", dest_path.name, tag)
            success_count += 1
            time.sleep(RATE_LIMIT_SLEEP)
        except Exception as e:
            log.error("  failed: %s — %s", pdf.name, e)
            error_count += 1

    log.info(
        "done: %d success, %d skipped, %d errors (of %d total)",
        success_count,
        skipped_count,
        error_count,
        len(pdfs),
    )


if __name__ == "__main__":
    main()
