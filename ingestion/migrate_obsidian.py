#!/usr/bin/env python3
"""Migrate Obsidian interview questions and AI System Design Guide into knowledge/obsidian/ with YAML frontmatter."""

import os
import sys
from pathlib import Path

SOURCE_INTERVIEW = Path("/home/anmol/Documents/Obsidian Vault/interview_questions")
SOURCE_DESIGN_GUIDE = Path("/home/anmol/Documents/Obsidian Vault/AI System Design Guide")
DEST_ROOT = Path("/home/anmol/Projects/Scholar-Loop/knowledge/obsidian")


def make_frontmatter(tags: list[str], topic: str = "obsidian") -> str:
    tag_lines = "\n".join(f"  - {t}" for t in tags)
    return (
        "---\n"
        "difficulty: medium\n"
        "last_sent:\n"
        "review_count: 0\n"
        f"tags:\n{tag_lines}\n"
        f"topic: {topic}\n"
        "---\n\n"
    )


def migrate_file(src: Path, dest: Path, frontmatter: str) -> bool:
    """Write file with frontmatter prepended. Returns True if written, False if skipped."""
    if dest.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    original = src.read_text(encoding="utf-8")
    dest.write_text(frontmatter + original, encoding="utf-8")
    return True


def migrate_interview_questions() -> int:
    count = 0
    for root, _dirs, files in os.walk(SOURCE_INTERVIEW):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            src = Path(root) / fname
            rel = src.relative_to(SOURCE_INTERVIEW)

            # Determine category from parent folder
            if rel.parent == Path("."):
                category = "general"
            else:
                category = str(rel.parent).replace(" ", "_").lower()

            tags = ["interview", category]
            dest = DEST_ROOT / "interview-questions" / rel
            if migrate_file(src, dest, make_frontmatter(tags)):
                count += 1
                print(f"  [interview] {rel}")
    return count


def migrate_design_guide() -> int:
    count = 0
    for root, _dirs, files in os.walk(SOURCE_DESIGN_GUIDE):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            src = Path(root) / fname
            rel = src.relative_to(SOURCE_DESIGN_GUIDE)
            dest = DEST_ROOT / "ai-system-design-guide" / rel
            tags = ["interview", "ai-system-design"]
            if migrate_file(src, dest, make_frontmatter(tags)):
                count += 1
                print(f"  [design-guide] {rel}")
    return count


def main():
    DEST_ROOT.mkdir(parents=True, exist_ok=True)

    print("=== Migrating interview questions ===")
    iq_count = migrate_interview_questions()
    print(f"\n=== Migrating AI System Design Guide ===")
    dg_count = migrate_design_guide()

    total = iq_count + dg_count
    print(f"\nDone. {iq_count} interview question files + {dg_count} design guide files = {total} files migrated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
