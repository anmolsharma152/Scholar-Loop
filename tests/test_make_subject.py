"""Tests for email subject line construction."""

from agent.send_daily import _make_subject


class TestMakeSubject:
    def test_learn_subject_no_topics(self):
        assert _make_subject("learn") == "\U0001f4dd Scholar-Loop"

    def test_quiz_subject_no_topics(self):
        assert _make_subject("quiz") == "\U0001f9e9 Scholar-Loop Quiz"

    def test_unknown_mode_falls_back_to_learn(self):
        assert _make_subject("other") == "\U0001f4dd Scholar-Loop"

    def test_learn_one_topic(self):
        assert _make_subject("learn", ["dsa"]) == "\U0001f4dd Scholar-Loop: Today's focus is on DSA"

    def test_two_topics_no_oxford_comma(self):
        s = _make_subject("quiz", ["dsa", "ml-ai"])
        assert s.endswith("DSA and ML")
        assert ", and" not in s

    def test_three_topics_oxford_comma(self):
        s = _make_subject("learn", ["dsa", "ml-ai", "system-design"])
        assert s.endswith("DSA, ML, and System Design")

    def test_duplicate_topics_deduped(self):
        s = _make_subject("learn", ["dsa", "dsa", "fullstack"])
        assert s.endswith("DSA and Fullstack")

    def test_daily_with_quiz(self):
        s = _make_subject("daily", ["system-design", "dsa"])
        assert s == "\U0001f4da Scholar-Loop: System Design and DSA \u2014 Learn & Quiz"

    def test_daily_without_quiz_drops_suffix(self):
        s = _make_subject("daily", ["dsa"], has_quiz=False)
        assert s == "\U0001f4da Scholar-Loop: DSA"
