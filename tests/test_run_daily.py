"""Tests for the combined daily email (Learn + Quiz) and quiz rotation. No network."""

import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

import agent.send_daily as mod
from agent.send_daily import _select_quiz_rows, get_db, run_daily

NOW = datetime(2026, 10, 5, 2, 0, tzinfo=timezone.utc)  # a Monday morning
FUTURE = (NOW + timedelta(days=10)).isoformat()
PAST = (NOW - timedelta(days=5)).isoformat()

FAKE_QA = (
    '<div class="quiz-q"><strong>Q1.</strong> A question?</div>',
    '<div class="quiz-answer"><strong>A1:</strong> An answer.</div>',
)


def _rel(tmp_knowledge_dir: Path, p: str) -> str:
    return str((tmp_knowledge_dir / p).relative_to(tmp_knowledge_dir.parent))


@pytest.fixture
def daily_db(tmp_knowledge_dir):
    """Two unsent notes (Learn candidates) and three sent notes (Quiz candidates)."""
    db_path = Path(tempfile.mktemp(suffix=".db"))
    mod.DB_PATH = db_path
    mod.KNOWLEDGE_DIR = tmp_knowledge_dir

    conn = get_db()  # creates schema incl. last_quizzed
    rows = [
        # path, title, topic, word_count, stability, due, review_count, last_sent, state, last_quizzed
        ("dsa/binary-search.md", "Binary Search", "dsa", 50, 1.0, None, 0, None, 1, None),
        ("system-design/caching.md", "Caching", "system-design", 45, 1.0, None, 0, None, 1, None),
        ("ml-ai/transformers.md", "Transformers", "ml-ai", 60, 5.0, FUTURE, 2, PAST, 2, None),
        ("fullstack/sql/joins.md", "SQL Joins", "fullstack", 55, 2.0, FUTURE, 2, PAST, 2, None),
        ("dsa/linked-list.md", "Linked List", "dsa", 40, 1.0, FUTURE, 2, PAST, 2, PAST),
    ]
    for path, title, topic, wc, stab, due, rc, last_sent, state, lq in rows:
        conn.execute(
            """INSERT INTO notes (path, title, topic, difficulty, tags, word_count, stability,
                                  difficulty_fsrs, due, review_count, last_sent, state, last_quizzed)
               VALUES (?, ?, ?, 'medium', '[]', ?, ?, 3.0, ?, ?, ?, ?, ?)""",
            (_rel(tmp_knowledge_dir, path), title, topic, wc, stab, due, rc, last_sent, state, lq),
        )
    conn.commit()
    conn.close()
    return db_path


def _row(db_path, title):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    r = conn.execute("SELECT * FROM notes WHERE title=?", (title,)).fetchone()
    conn.close()
    return r


class TestRunDaily:
    def test_combined_email_has_learn_quiz_and_answers(self, daily_db):
        sent = []
        with patch("agent.send_daily.generate_quiz_qas", return_value=FAKE_QA):
            ok = run_daily(dry_run=False, now=NOW,
                           send_fn=lambda s, h, send_at=None: sent.append((s, h)))

        assert ok is True
        assert len(sent) == 1
        subject, html = sent[0]
        assert subject.startswith("\U0001f4da Scholar-Loop:")
        assert subject.endswith("Learn & Quiz")
        assert "Today's notes" in html
        assert "Active recall" in html
        assert "Answers" in html
        # Learn notes come before the quiz, answers come last.
        assert html.index("Today's notes") < html.index("Active recall") < html.index("Answers")

    def test_quiz_never_repeats_todays_learn_notes(self, daily_db):
        conn = sqlite3.connect(str(daily_db))
        conn.row_factory = sqlite3.Row
        learn_ids = {r["id"] for r in conn.execute("SELECT id FROM notes WHERE last_sent IS NULL")}
        quiz = _select_quiz_rows(conn, 5, exclude_ids=learn_ids)
        conn.close()
        assert learn_ids.isdisjoint({r["id"] for r in quiz})

    def test_state_updates_after_send(self, daily_db):
        with patch("agent.send_daily.generate_quiz_qas", return_value=FAKE_QA):
            run_daily(dry_run=False, now=NOW, send_fn=lambda *a, **k: None)

        # Learn notes get an FSRS review.
        bs = _row(daily_db, "Binary Search")
        assert bs["review_count"] == 1 and bs["last_sent"] is not None
        # Quiz notes are rotated but FSRS state is untouched.
        joins = _row(daily_db, "SQL Joins")
        assert joins["last_quizzed"] == NOW.isoformat()
        assert joins["review_count"] == 2 and joins["due"] == FUTURE

    def test_quiz_failure_still_sends_learn_notes(self, daily_db, capsys):
        sent = []
        with patch("agent.send_daily.generate_quiz_qas", return_value=None):
            ok = run_daily(dry_run=False, now=NOW,
                           send_fn=lambda s, h, send_at=None: sent.append((s, h)))

        assert ok is True
        subject, html = sent[0]
        assert "Learn & Quiz" not in subject
        assert "Quiz unavailable today" in html
        assert "::warning" in capsys.readouterr().out
        # Failed quiz notes are not marked as quizzed.
        assert _row(daily_db, "SQL Joins")["last_quizzed"] is None

    def test_dry_run_sends_nothing_and_changes_nothing(self, daily_db):
        sent = []
        ok = run_daily(dry_run=True, now=NOW, send_fn=lambda *a, **k: sent.append(1))
        assert ok is True
        assert sent == []
        assert _row(daily_db, "Binary Search")["review_count"] == 0


class TestQuizRotation:
    def test_least_recently_quizzed_then_weakest_first(self, daily_db):
        conn = sqlite3.connect(str(daily_db))
        conn.row_factory = sqlite3.Row
        picked = [r["title"] for r in _select_quiz_rows(conn, 3)]
        conn.close()
        # Never-quizzed notes first (weakest first), recently quizzed Linked List last.
        assert picked == ["SQL Joins", "Transformers", "Linked List"]

    def test_one_note_per_topic_before_repeating(self, daily_db):
        conn = sqlite3.connect(str(daily_db))
        conn.row_factory = sqlite3.Row
        topics = [r["topic"] for r in _select_quiz_rows(conn, 3)]
        conn.close()
        assert len(set(topics)) == 3


class TestLlmRouter:
    def test_missing_key_raises(self, monkeypatch):
        from agent import llm_router
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
            llm_router.chat_completion_with_fallback([{"role": "user", "content": "hi"}])

    def test_flash_latest_alias_is_primary(self, monkeypatch):
        from agent import llm_router
        monkeypatch.delenv("LLM_MODEL", raising=False)
        assert llm_router.get_models()[0] == "gemini-flash-latest"

    def test_llm_model_override_goes_first(self, monkeypatch):
        from agent import llm_router
        monkeypatch.setenv("LLM_MODEL", "gemini-3.8-flash")
        models = llm_router.get_models()
        assert models[0] == "gemini-3.8-flash"
        assert models.count("gemini-3.8-flash") == 1
