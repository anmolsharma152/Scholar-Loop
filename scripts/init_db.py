#!/usr/bin/env python3
"""Create the SQLite database and migrate existing frontmatter state."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import frontmatter

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "user.db"
TOPIC_DIRS = ["dsa", "system-design", "ml-ai", "fullstack", "papers"]
SKIP_FILES = {"README.md"}


def create_schema(conn: sqlite3.Connection):
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
    # Migrate older DBs that predate FSRS state/step columns.
    cols = {r[1] for r in conn.execute("PRAGMA table_info(notes)")}
    if "state" not in cols:
        conn.execute("ALTER TABLE notes ADD COLUMN state INTEGER DEFAULT 1")
    if "step" not in cols:
        conn.execute("ALTER TABLE notes ADD COLUMN step INTEGER")
    conn.execute("""
        UPDATE notes
        SET state = 2, step = NULL
        WHERE last_sent IS NOT NULL
          AND review_count > 0
          AND (state IS NULL OR state = 1)
    """)
    conn.commit()


def _prune_deleted(conn: sqlite3.Connection):
    """Remove DB entries for files that no longer exist in topic directories."""
    existing_paths = set()
    for topic in TOPIC_DIRS:
        topic_dir = KNOWLEDGE_DIR / topic
        if not topic_dir.exists():
            continue
        for md_path in topic_dir.rglob("*.md"):
            if md_path.name in SKIP_FILES:
                continue
            rel_path = str(md_path.relative_to(KNOWLEDGE_DIR.parent))
            existing_paths.add(rel_path)

    deleted = conn.execute(
        "DELETE FROM notes WHERE path NOT IN ({})".format(
            ",".join("?" for _ in existing_paths)
        ),
        tuple(existing_paths),
    ).rowcount
    if deleted:
        print(f"  Pruned {deleted} orphaned DB entries")
    conn.commit()


def migrate_frontmatter(conn: sqlite3.Connection):
    """Read all markdown notes and insert into DB, preserving existing state."""
    inserted = 0
    updated = 0

    for topic in TOPIC_DIRS:
        topic_dir = KNOWLEDGE_DIR / topic
        if not topic_dir.exists():
            continue
        for md_path in sorted(topic_dir.rglob("*.md")):
            if md_path.name in SKIP_FILES:
                continue

            post = frontmatter.load(str(md_path))
            meta = post.metadata
            rel_path = str(md_path.relative_to(KNOWLEDGE_DIR.parent))

            title = _extract_title(post.content, md_path)
            difficulty = meta.get("difficulty", "medium")
            tags = json.dumps(meta.get("tags", []))
            word_count = len(post.content.split())
            sequence = meta.get("sequence")
            last_sent = meta.get("last_sent")
            review_count = meta.get("review_count") or 0

            # Check if already in DB
            existing = conn.execute(
                "SELECT id FROM notes WHERE path = ?", (rel_path,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE notes SET
                        title = ?, topic = ?, difficulty = ?, tags = ?,
                        word_count = ?, sequence = ?, review_count = ?,
                        last_sent = ?
                    WHERE path = ?
                """, (title, topic, difficulty, tags, word_count,
                      sequence, review_count,
                      last_sent.isoformat() if last_sent else None,
                      rel_path))
                updated += 1
            else:
                conn.execute("""
                    INSERT INTO notes (path, title, topic, difficulty, tags,
                        word_count, sequence, review_count, last_sent, due)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (rel_path, title, topic, difficulty, tags,
                      word_count, sequence, review_count,
                      last_sent.isoformat() if last_sent else None,
                      last_sent.isoformat() if last_sent else None))
                inserted += 1

    conn.commit()
    return inserted, updated


def _extract_title(content: str, path: Path) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    print("Creating schema...")
    create_schema(conn)

    print("Pruning stale entries...")
    _prune_deleted(conn)

    print("Migrating frontmatter state...")
    inserted, updated = migrate_frontmatter(conn)

    total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    print(f"Done. {total} notes in DB ({inserted} new, {updated} updated)")

    # Show topic distribution
    rows = conn.execute(
        "SELECT topic, COUNT(*) FROM notes GROUP BY topic ORDER BY COUNT(*) DESC"
    ).fetchall()
    for topic, count in rows:
        print(f"  {topic}: {count}")

    conn.close()


if __name__ == "__main__":
    main()
