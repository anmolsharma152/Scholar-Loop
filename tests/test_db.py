"""Tests for DB helper functions (count_due, pick_due_notes, mark_sent)."""

from datetime import datetime, timezone, timedelta

import pytest

from agent.send_daily import count_due, pick_due_notes, mark_sent


class TestCountDue:
    def test_empty_db_empty_result(self, empty_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        assert count_due(empty_db, "dsa", now) == 0

    def test_all_null_due_counted(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        assert count_due(seeded_db, "dsa", now) == 2

    def test_some_due_some_not(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        seeded_db.execute(
            "UPDATE notes SET due=? WHERE path=?",
            ("2026-07-20T00:00:00", "knowledge/dsa/binary-search.md")
        )
        seeded_db.commit()
        assert count_due(seeded_db, "dsa", now) == 1

    def test_past_due_counted(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        seeded_db.execute(
            "UPDATE notes SET due=? WHERE path=?",
            ("2026-07-10T00:00:00", "knowledge/dsa/binary-search.md")
        )
        seeded_db.commit()
        assert count_due(seeded_db, "dsa", now) == 2


class TestPickDueNotes:
    def test_pick_single(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        rows = pick_due_notes(seeded_db, "dsa", 1, now=now)
        assert len(rows) == 1
        assert rows[0]["topic"] == "dsa"

    def test_pick_many(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        rows = pick_due_notes(seeded_db, "dsa", 5, now=now)
        assert len(rows) == 2  # only 2 dsa notes

    def test_exclude_ids(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        first = seeded_db.execute(
            "SELECT id FROM notes WHERE topic=? LIMIT 1", ("dsa",)
        ).fetchone()[0]
        rows = pick_due_notes(seeded_db, "dsa", 5, exclude_ids={first}, now=now)
        assert len(rows) == 1
        assert rows[0]["id"] != first

    def test_only_due_returned(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        seeded_db.execute(
            "UPDATE notes SET due=? WHERE path=?",
            ("2026-07-20T00:00:00", "knowledge/dsa/binary-search.md")
        )
        seeded_db.commit()
        rows = pick_due_notes(seeded_db, "dsa", 5, now=now)
        assert len(rows) == 1

    def test_sequence_gates_unsent_notes(self, empty_db):
        """Unsent notes only at min sequence; higher sequences blocked."""
        conn = empty_db
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        for path, title, seq in [
            ("knowledge/dsa/calc.md", "Calc", 1),
            ("knowledge/dsa/arrays.md", "Arrays", 4),
            ("knowledge/dsa/trie.md", "Trie", 18),
        ]:
            conn.execute(
                """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
                   stability, difficulty_fsrs, due, review_count, last_sent, sequence, state)
                   VALUES (?, ?, 'dsa', 'easy', '[]', 10, 1.0, 3.0, NULL, 0, NULL, ?, 1)""",
                (path, title, seq),
            )
        conn.commit()

        rows = pick_due_notes(conn, "dsa", 5, now=now)
        assert len(rows) == 1
        assert rows[0]["title"] == "Calc"
        assert rows[0]["sequence"] == 1

    def test_sequence_allows_reviews_regardless(self, empty_db):
        """Already-sent due reviews pass the sequence gate."""
        conn = empty_db
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        past = (now - timedelta(days=1)).isoformat()
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent, sequence, state)
               VALUES (?, ?, 'dsa', 'easy', '[]', 10, 2.3, 3.0, ?, 1, ?, 18, 2)""",
            ("knowledge/dsa/trie.md", "Trie", past, past),
        )
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent, sequence, state)
               VALUES (?, ?, 'dsa', 'easy', '[]', 10, 1.0, 3.0, NULL, 0, NULL, 1, 1)""",
            ("knowledge/dsa/calc.md", "Calc"),
        )
        conn.commit()

        rows = pick_due_notes(conn, "dsa", 5, now=now)
        titles = {r["title"] for r in rows}
        assert titles == {"Trie", "Calc"}

    def test_sequence_prefers_new_curriculum_over_reviews(self, empty_db):
        """When a sequence gate is open, introduce next syllabus note first."""
        conn = empty_db
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        past = (now - timedelta(days=1)).isoformat()
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent, sequence, state)
               VALUES (?, ?, 'dsa', 'easy', '[]', 10, 2.3, 3.0, ?, 1, ?, 18, 2)""",
            ("knowledge/dsa/trie.md", "Trie", past, past),
        )
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count,
               stability, difficulty_fsrs, due, review_count, last_sent, sequence, state)
               VALUES (?, ?, 'dsa', 'easy', '[]', 10, 1.0, 3.0, NULL, 0, NULL, 1, 1)""",
            ("knowledge/dsa/calc.md", "Calc"),
        )
        conn.commit()

        rows = pick_due_notes(conn, "dsa", 1, now=now)
        assert len(rows) == 1
        assert rows[0]["title"] == "Calc"


class TestMarkSent:
    def test_mark_sent_updates_fields(self, seeded_db):
        now = datetime(2026, 7, 16, tzinfo=timezone.utc)
        row = seeded_db.execute(
            "SELECT id, review_count FROM notes LIMIT 1"
        ).fetchone()
        note_id, prev_count = row["id"], row["review_count"]

        mark_sent(seeded_db, note_id, now)

        updated = seeded_db.execute(
            "SELECT * FROM notes WHERE id=?", (note_id,)
        ).fetchone()
        assert updated["last_sent"] == now.isoformat()
        assert updated["review_count"] == prev_count + 1
        # Passive Good must schedule a future due date (not "due now")
        due = datetime.fromisoformat(updated["due"])
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        assert due > now
        assert (due - now).total_seconds() >= 86400  # at least ~1 day
        assert updated["stability"] is not None and updated["stability"] > 0
        assert updated["state"] == 2  # Review

        reviews = seeded_db.execute(
            "SELECT grade FROM reviews WHERE note_id=?", (note_id,)
        ).fetchall()
        assert len(reviews) == 1
        assert reviews[0]["grade"] == 3  # Rating.Good

    def test_second_review_advances_interval(self, seeded_db):
        t0 = datetime(2026, 7, 16, tzinfo=timezone.utc)
        note_id = seeded_db.execute("SELECT id FROM notes LIMIT 1").fetchone()["id"]

        mark_sent(seeded_db, note_id, t0)
        row1 = seeded_db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        due1 = datetime.fromisoformat(row1["due"])
        if due1.tzinfo is None:
            due1 = due1.replace(tzinfo=timezone.utc)

        mark_sent(seeded_db, note_id, due1)
        row2 = seeded_db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        due2 = datetime.fromisoformat(row2["due"])
        if due2.tzinfo is None:
            due2 = due2.replace(tzinfo=timezone.utc)

        assert row2["review_count"] == 2
        assert due2 > due1
        assert (due2 - due1).total_seconds() > (due1 - t0).total_seconds()
