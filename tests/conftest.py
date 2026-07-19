import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import pytest


# Tell init_db where to find notes by overriding its KNOWLEDGE_DIR at module level
@pytest.fixture(autouse=True)
def _patch_knowledge_dir(tmp_knowledge_dir):
    """Patch scripts.init_db.KNOWLEDGE_DIR to use the temp fixture dir."""
    import scripts.init_db as init_mod
    import agent.send_daily as send_mod
    orig_init_kd = init_mod.KNOWLEDGE_DIR
    orig_send_kd = send_mod.KNOWLEDGE_DIR

    init_mod.KNOWLEDGE_DIR = tmp_knowledge_dir
    send_mod.KNOWLEDGE_DIR = tmp_knowledge_dir

    yield

    init_mod.KNOWLEDGE_DIR = orig_init_kd
    send_mod.KNOWLEDGE_DIR = orig_send_kd


@pytest.fixture
def tmp_knowledge_dir():
    """Create a temporary knowledge directory with test .md files."""
    tmp = Path(tempfile.mkdtemp())
    topics = ["dsa", "ml-ai", "system-design", "fullstack"]
    for t in topics:
        (tmp / t).mkdir(parents=True)
    # sql is now a subdirectory of fullstack
    (tmp / "fullstack" / "sql").mkdir(parents=True)

    notes = {
        "dsa/binary-search.md": """---
difficulty: medium
tags: ["search", "binary"]
---
# Binary Search

Binary search finds an element in O(log n) time.

Time complexity: O(log n)
Space complexity: O(1)

## Key takeaways
- Requires sorted array
- Divide and conquer approach""",

        "dsa/linked-list.md": """---
difficulty: easy
tags: ["linked-list", "pointers"]
---
# Linked List

A linked list is a linear data structure.

Each node contains data and a pointer to the next node.

## Key takeaways
- Dynamic size
- No random access""",

        "ml-ai/transformers.md": """---
difficulty: hard
tags: ["deep-learning", "nlp"]
---
# Transformers

Transformer architecture uses self-attention mechanisms.

## Key components
- Multi-head attention
- Feed-forward networks
- Positional encoding""",

        "fullstack/sql/joins.md": """---
difficulty: medium
tags: ["sql", "joins"]
---
# SQL Joins

SQL joins combine rows from multiple tables.

## Types
- INNER JOIN: matching rows only
- LEFT JOIN: all from left table
- RIGHT JOIN: all from right table
- FULL OUTER JOIN: all from both""",

        "system-design/caching.md": """---
difficulty: medium
tags: ["caching", "performance"]
---
# Caching

Caching stores frequently accessed data in memory.

## Strategies
- Cache-aside
- Write-through
- Write-behind""",
    }

    for rel_path, content in notes.items():
        fpath = tmp / rel_path
        fpath.write_text(content)

    yield tmp
    shutil.rmtree(str(tmp))


@pytest.fixture
def db_path():
    """Return a path for a transient test DB."""
    return Path(tempfile.mktemp(suffix=".db"))


@pytest.fixture
def empty_db(db_path):
    """Create an empty notes DB with the schema, using Row factory."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
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
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER REFERENCES notes(id),
            sent_at TEXT NOT NULL,
            grade INTEGER NOT NULL,
            response_time_ms INTEGER
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_topic ON notes(topic)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_due ON notes(due)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_note ON reviews(note_id)")
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def seeded_db(empty_db):
    """DB with sample notes seeded."""
    conn = empty_db
    # path, title, topic, difficulty, tags, word_count, stability, difficulty_fsrs,
    # due, review_count, last_sent, sequence, state, step
    # sequence=None so default pick tests are not gated by curriculum order.
    notes = [
        ("knowledge/dsa/binary-search.md", "Binary Search", "dsa", "medium",
         '["search","binary"]', 50, 3.0, 3.0, None, 0, None, None, 1, None),
        ("knowledge/dsa/linked-list.md", "Linked List", "dsa", "easy",
         '["linked-list"]', 40, 8.0, 2.0, None, 0, None, None, 1, None),
        ("knowledge/ml-ai/transformers.md", "Transformers", "ml-ai", "hard",
         '["deep-learning","nlp"]', 60, 12.0, 5.0, None, 0, None, None, 1, None),
        ("knowledge/sql/joins.md", "SQL Joins", "sql", "medium",
         '["sql","joins"]', 55, 5.0, 4.0, None, 0, None, None, 1, None),
        ("knowledge/system-design/caching.md", "Caching", "system-design", "medium",
         '["caching","performance"]', 45, 7.0, 3.5, None, 0, None, None, 1, None),
    ]
    for n in notes:
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent,
               sequence, state, step)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            n
        )
    conn.commit()
    return conn
