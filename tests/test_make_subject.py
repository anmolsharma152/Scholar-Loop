"""Tests for email subject line construction (fixed format with emoji)."""

from agent.send_daily import _make_subject


class TestMakeSubject:
    def test_learn_subject(self):
        s = _make_subject("learn")
        assert s == "\U0001f4dd Scholar-Loop"

    def test_quiz_subject(self):
        s = _make_subject("quiz")
        assert s == "\U0001f9e9 Scholar-Loop Quiz"

    def test_unknown_mode_subject(self):
        s = _make_subject("other")
        assert s == "\U0001f4dd Scholar-Loop"
