"""Tests for email subject line construction."""

from agent.send_daily import _make_subject


class TestMakeSubject:
    def test_one_title(self):
        assert _make_subject("", ["Binary"]) == "Scholar-Loop: Binary"

    def test_two_titles(self):
        assert _make_subject("", ["Binary", "Linked"]) == "Scholar-Loop: Binary, Linked"

    def test_three_shows_all(self):
        s = _make_subject("", ["A", "B", "C"])
        assert ", ".join(["A", "B", "C"]) in s
        assert "+" not in s

    def test_four_shows_all(self):
        # Truncation only kicks in at 5+ titles
        s = _make_subject("", ["A", "B", "C", "D"])
        assert s == "Scholar-Loop: A, B, C, D"
        assert "+" not in s

    def test_five_uses_plus_more(self):
        s = _make_subject("", ["A", "B", "C", "D", "E"])
        assert "A, B, C" in s
        assert "+2 more" in s

    def test_quiz_prefix(self):
        s = _make_subject("Quiz", ["A"])
        assert "Scholar-Loop Quiz:" in s
