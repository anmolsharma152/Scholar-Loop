"""Tests for init_db schema, migration, and pruning."""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from scripts.init_db import create_schema, migrate_frontmatter, _prune_deleted


class TestCreateSchema:
    def test_tables_created(self, empty_db):
        tables = empty_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = {r[0] for r in tables}
        assert "notes" in names
        assert "reviews" in names

    def test_columns_exist(self, empty_db):
        cols = {r[1] for r in empty_db.execute("PRAGMA table_info(notes)")}
        for col in ("id", "path", "title", "topic", "due", "stability",
                     "difficulty_fsrs", "review_count", "last_sent",
                     "elapsed_days", "created_at", "state", "step", "sequence"):
            assert col in cols

    def test_indexes_created(self, empty_db):
        idxs = {r[1] for r in empty_db.execute("PRAGMA index_list(notes)")}
        for idx in ("idx_notes_topic", "idx_notes_due"):
            assert idx in idxs


class TestMigrateFrontmatter:
    def test_inserts_new_notes(self, tmp_knowledge_dir):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = sqlite3.connect(str(db_path))
        create_schema(conn)

        inserted, updated = migrate_frontmatter(conn)
        assert inserted == 5  # 5 fixture files
        assert updated == 0

        count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        assert count == 5
        conn.close()

    def test_updates_existing_notes(self, tmp_knowledge_dir):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = sqlite3.connect(str(db_path))
        create_schema(conn)

        # Insert first pass
        migrate_frontmatter(conn)

        # Second pass should update, not insert
        inserted, updated = migrate_frontmatter(conn)
        assert inserted == 0
        assert updated == 5

        count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        assert count == 5
        conn.close()

    def test_preserves_fsrs_fields_on_update(self, tmp_knowledge_dir):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = sqlite3.connect(str(db_path))
        create_schema(conn)
        migrate_frontmatter(conn)

        # Set custom FSRS state
        conn.execute(
            "UPDATE notes SET stability=99.9, difficulty_fsrs=8.5, due='2026-08-01T00:00:00'"
        )
        conn.commit()

        # Re-migrate
        migrate_frontmatter(conn)

        # FSRS state should be preserved
        row = conn.execute("SELECT stability, difficulty_fsrs FROM notes LIMIT 1").fetchone()
        assert row[0] == 99.9
        assert row[1] == 8.5
        conn.close()

    def test_inserts_generates_id(self, tmp_knowledge_dir):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = sqlite3.connect(str(db_path))
        create_schema(conn)
        migrate_frontmatter(conn)

        ids = conn.execute("SELECT id FROM notes ORDER BY id").fetchall()
        # Auto-increment should produce sequential IDs
        for i, (row_id,) in enumerate(ids):
            assert row_id == i + 1
        conn.close()


class TestPruneDeleted:
    def test_removes_orphaned_entries(self, tmp_knowledge_dir, empty_db):
        conn = empty_db
        conn.execute(
            """INSERT INTO notes (path, title, topic)
               VALUES (?, ?, ?)""",
            ("knowledge/dsa/deleted.md", "Deleted", "dsa")
        )
        conn.commit()
        count_before = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        assert count_before == 1

        _prune_deleted(conn)

        count_after = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        assert count_after == 0
        conn.close()

    def test_keeps_existing_entries(self, tmp_knowledge_dir):
        db_path = Path(tempfile.mktemp(suffix=".db"))
        conn = sqlite3.connect(str(db_path))
        create_schema(conn)
        migrate_frontmatter(conn)

        count_before = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        _prune_deleted(conn)
        count_after = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        assert count_after == count_before
        conn.close()
