#!/usr/bin/env python3
"""Intelligently ingest and chunk massive Obsidian markdown files into Scholar-Loop.

Usage:
  python scripts/ingest_obsidian.py <input_file> <target_topic>

Example:
  python scripts/ingest_obsidian.py knowledge/obsidian/ai-system-design-guide/01-foundations/what_is_ai.md ml-ai
"""

import os
import sys
import json
from pathlib import Path
from openai import OpenAI

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

def process_file(input_path: Path, target_topic: str):
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY must be set.", file=sys.stderr)
        sys.exit(1)

    if not input_path.exists():
        print(f"Error: {input_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    target_dir = KNOWLEDGE_DIR / target_topic
    if not target_dir.exists():
        print(f"Error: Target topic '{target_topic}' does not exist in {KNOWLEDGE_DIR}.", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content) > 20000:
        print(f"Warning: File is very large ({len(content)} chars). Consider splitting manually first or risk LLM truncation.")

    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
    
    prompt = f"""You are an expert knowledge base structurer. Your job is to take a large, raw Markdown study guide and break it down into a list of smaller, self-contained, atomic "flashcard" notes.

Each sub-note should be roughly 50-150 lines and focus on one specific concept.
For each sub-note, provide a highly descriptive filename (e.g. `vector-databases-indexing.md`) and the full markdown content including YAML frontmatter.

The YAML frontmatter MUST look exactly like this:
---
difficulty: medium
tags:
  - your-tags-here
---
# Descriptive Title Here

Then the markdown content follows.

Output your response as a JSON object containing a "notes" array, where each object has "filename" and "content".
Example output format:
{{
  "notes": [
    {{
      "filename": "concept-one-basics.md",
      "content": "---\ndifficulty: easy\ntags:\n  - ai\n---\n# Concept One\n\nContent here..."
    }},
    {{
      "filename": "concept-two-advanced.md",
      "content": "---\ndifficulty: hard\ntags:\n  - advanced\n---\n# Concept Two\n\nContent here..."
    }}
  ]
}}

Here is the raw document to process:
-----------------------------------------
{content[:25000]}
"""

    print(f"Processing {input_path.name} via Groq ({LLM_MODEL})... This may take a minute.")
    
    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        print(f"Failed to call Groq: {e}", file=sys.stderr)
        sys.exit(1)

    result_text = resp.choices[0].message.content.strip()
    
    try:
        data = json.loads(result_text)
        notes_list = data.get("notes", [])
        if not notes_list:
            print("Error: Could not find 'notes' array in the JSON response.")
            sys.exit(1)

    except json.JSONDecodeError:
        print("Error: LLM did not return valid JSON.", file=sys.stderr)
        print("Raw output:")
        print(result_text)
        sys.exit(1)

    print(f"Successfully chunked into {len(notes_list)} atomic notes.")
    
    for note in notes_list:
        filename = note.get("filename", "").replace(" ", "-").lower()
        if not filename.endswith(".md"):
            filename += ".md"
        content = note.get("content", "")
        
        if not filename or not content:
            print("Skipping malformed note object.")
            continue
            
        out_path = target_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  -> Created {out_path.relative_to(KNOWLEDGE_DIR)}")
        
    print("\nRemember to run `python scripts/init_db.py` to index the new notes!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/ingest_obsidian.py <input_file> <target_topic>")
        sys.exit(1)
        
    input_file = Path(sys.argv[1])
    target = sys.argv[2]
    
    process_file(input_file, target)
