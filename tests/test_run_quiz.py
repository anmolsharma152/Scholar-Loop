"""Tests for run_quiz logic (injectable send_fn, no network)."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

from agent.send_daily import run_quiz


_SCHEMA = """
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
"""


def _create_db_with_schema(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


class TestRunQuiz:
    def test_dry_run_returns_true(self, seeded_db):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        import agent.send_daily as mod
        mod.DB_PATH = db_path

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.executescript(_SCHEMA)
        notes = [
            ("knowledge/dsa/binary-search.md", "Binary Search", "dsa", "medium",
             '["search","binary"]', 50, 3.0, 3.0, None, 0, None),
            ("knowledge/dsa/linked-list.md", "Linked List", "dsa", "easy",
             '["linked-list"]', 40, 8.0, 2.0, None, 0, None),
            ("knowledge/ml-ai/transformers.md", "Transformers", "ml-ai", "hard",
             '["deep-learning","nlp"]', 60, 12.0, 5.0, None, 0, None),
            ("knowledge/sql/joins.md", "SQL Joins", "sql", "medium",
             '["sql","joins"]', 55, 5.0, 4.0, None, 0, None),
            ("knowledge/system-design/caching.md", "Caching", "system-design", "medium",
             '["caching","performance"]', 45, 7.0, 3.5, None, 0, None),
        ]
        for n in notes:
            conn.execute(
                """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
                   stability, difficulty_fsrs, due, review_count, last_sent)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                n
            )
        conn.commit()
        conn.close()

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        result = run_quiz(dry_run=True, now=now)
        assert result is True

    def test_empty_db_fallback(self):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        import agent.send_daily as mod
        mod.DB_PATH = db_path

        conn = _create_db_with_schema(db_path)
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("test.md", "Test", "dsa", "easy", "[]", 10,
             3.0, 3.0, None, 0, None)
        )
        conn.commit()
        conn.close()

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        result = run_quiz(dry_run=True, now=now)
        assert result is True

    def test_empty_db_no_notes_returns_false(self):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        import agent.send_daily as mod
        mod.DB_PATH = db_path

        conn = _create_db_with_schema(db_path)
        conn.close()

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        result = run_quiz(dry_run=True, now=now)
        assert result is False

    def test_sends_immediate_email(self, tmp_knowledge_dir):
        """Quiz sends immediately (dual cron); no Resend scheduled_at."""
        db_path = Path(tempfile.mktemp(suffix=".db"))
        import agent.send_daily as mod
        mod.DB_PATH = db_path
        # Paths are relative to KNOWLEDGE_DIR.parent (same as init_db migrate).
        mod.KNOWLEDGE_DIR = tmp_knowledge_dir
        rel_path = str((tmp_knowledge_dir / "dsa" / "binary-search.md").relative_to(
            tmp_knowledge_dir.parent
        ))

        conn = _create_db_with_schema(db_path)
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent, state)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (rel_path, "Binary Search", "dsa", "medium",
             '["search","binary"]', 50, 3.0, 3.0, now.isoformat(), 1, now.isoformat(), 2),
        )
        conn.commit()
        conn.close()

        sent = []

        def fake_send(subj, html, send_at=None):
            sent.append({"subj": subj, "html": html, "send_at": send_at})

        fake_qa = (
            'Q1. What is binary search?\n'
            '<div class="quiz-answer"><span class="answer-label">Answer:</span> O(log n)</div>\n'
            'Q2. Requirement?\n'
            '<div class="quiz-answer"><span class="answer-label">Answer:</span> sorted array</div>\n'
            'Q3. Complexity?\n'
            '<div class="quiz-answer"><span class="answer-label">Answer:</span> logarithmic</div>'
        )

        with patch("agent.send_daily.generate_quiz_qas", return_value=fake_qa):
            result = run_quiz(dry_run=False, now=now, send_fn=fake_send)

        assert result is True
        assert len(sent) == 1
        assert sent[0]["send_at"] is None  # dual-cron: send now
        assert "\U0001f9e9 Scholar-Loop Quiz" in sent[0]["subj"]
        assert "quiz-answer" in sent[0]["html"]
