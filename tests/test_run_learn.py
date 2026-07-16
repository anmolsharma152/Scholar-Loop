"""Tests for run_learn logic (injectable send_fn, no network)."""

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import sqlite3

import pytest

from agent.send_daily import run_learn
from scripts.init_db import create_schema, migrate_frontmatter


def _test_db(knowledge_base):
    """Create a test DB from a knowledge tree."""
    db = Path(tempfile.mktemp(suffix=".db"))
    conn = sqlite3.connect(str(db))
    create_schema(conn)
    inserted, updated = migrate_frontmatter(conn)
    conn.close()
    return db


class TestRunLearn:
    def test_dry_run_no_email(self, tmp_knowledge_dir):
        """Dry run should not call send_fn."""
        db = _test_db(tmp_knowledge_dir)
        import agent.send_daily as mod
        mod.DB_PATH = db

        sent_emails = []
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)

        def fake_send(subj, html, send_at=None):
            sent_emails.append((subj, send_at))

        result = run_learn(dry_run=True, now=now, send_fn=fake_send)
        assert result is True
        assert len(sent_emails) == 0

    def test_dry_run_returns_bool(self, tmp_knowledge_dir):
        db = _test_db(tmp_knowledge_dir)
        import agent.send_daily as mod
        mod.DB_PATH = db
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        result = run_learn(dry_run=True, now=now)
        assert result is True

    def test_picks_notes_and_calls_send(self, tmp_knowledge_dir):
        db = _test_db(tmp_knowledge_dir)
        import agent.send_daily as mod
        mod.DB_PATH = db

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        sent_emails = []

        def fake_send(subj, html, send_at=None):
            sent_emails.append({"subj": subj, "html": html, "send_at": send_at})

        result = run_learn(dry_run=False, now=now, send_fn=fake_send)
        assert result is True
        assert len(sent_emails) == 1
        assert sent_emails[0]["send_at"] is None

        html = sent_emails[0]["html"]
        assert "Scholar-Loop" in html
        assert "<!DOCTYPE html>" in html
        assert "note-section" in html

    def test_marks_notes_sent_in_db(self, tmp_knowledge_dir):
        db = _test_db(tmp_knowledge_dir)
        import agent.send_daily as mod
        mod.DB_PATH = db

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)

        def fake_send(subj, html, send_at=None):
            pass

        run_learn(dry_run=False, now=now, send_fn=fake_send)

        conn = sqlite3.connect(str(db))
        total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        unsent = conn.execute(
            "SELECT COUNT(*) FROM notes WHERE last_sent IS NULL"
        ).fetchone()[0]
        conn.close()
        assert total - unsent > 0

    def test_no_due_notes_returns_false(self):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                due TEXT,
                stability REAL DEFAULT 1.0,
                difficulty_fsrs REAL DEFAULT 3.0,
                review_count INTEGER DEFAULT 0,
                last_sent TEXT,
                difficulty TEXT,
                tags TEXT,
                word_count INTEGER,
                sequence INTEGER,
                state INTEGER DEFAULT 1,
                step INTEGER,
                elapsed_days INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent, state)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("test.md", "Test", "dsa", "easy", "[]", 10,
             3.0, 3.0, "2099-01-01T00:00:00", 0, "2099-01-01T00:00:00", 2)
        )
        conn.commit()
        conn.close()

        import agent.send_daily as mod
        mod.DB_PATH = db_path

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        result = run_learn(dry_run=True, now=now)
        assert result is False

    def test_mark_sent_schedules_future_due(self, tmp_knowledge_dir):
        db = _test_db(tmp_knowledge_dir)
        import agent.send_daily as mod
        mod.DB_PATH = db

        now = datetime(2026, 7, 16, tzinfo=timezone.utc)

        def fake_send(subj, html, send_at=None):
            pass

        run_learn(dry_run=False, now=now, send_fn=fake_send)

        conn = sqlite3.connect(str(db))
        rows = conn.execute(
            "SELECT due, last_sent, stability, state, review_count FROM notes WHERE last_sent IS NOT NULL"
        ).fetchall()
        conn.close()
        assert rows
        for due_s, last_s, stab, state, rc in rows:
            due = datetime.fromisoformat(due_s)
            last = datetime.fromisoformat(last_s)
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            assert due > last
            assert stab and stab > 1.0
            assert state == 2
            assert rc >= 1
