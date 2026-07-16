"""Tests for topic slot allocation logic."""

from agent.send_daily import compute_topic_slots, TOPIC_WEIGHTS


class TestComputeTopicSlots:
    def test_allocates_from_weights(self):
        def count_fn(topic):
            return {"dsa": 10, "sql": 10}.get(topic, 0)

        slots = compute_topic_slots(
            {"dsa": 0.8, "sql": 0.2}, 4, count_fn
        )
        assert slots["dsa"] == 3  # round(4 * 0.8) = 3
        assert slots["sql"] == 1  # round(4 * 0.2) = 1

    def test_caps_at_available(self):
        def count_fn(topic):
            return {"dsa": 1}.get(topic, 0)

        slots = compute_topic_slots(
            {"dsa": 0.9, "sql": 0.1}, 4, count_fn
        )
        assert slots["dsa"] == 1  # only 1 available
        assert "sql" not in slots  # 0 available

    def test_empty_topic_omitted(self):
        def count_fn(topic):
            return 0

        slots = compute_topic_slots(TOPIC_WEIGHTS, 4, count_fn)
        assert slots == {}

    def test_rounding_undershoot_filled(self):
        def count_fn(topic):
            return {"dsa": 10, "sql": 10}.get(topic, 10)

        slots = compute_topic_slots(
            {"dsa": 0.35, "sql": 0.30, "ml-ai": 0.35}, 4, count_fn
        )
        # round(4*0.35)=1, round(4*0.30)=1, round(4*0.35)=1 => 3 filled, 1 remaining
        assert sum(slots.values()) == 4

    def test_respects_total_slots_cap(self):
        def count_fn(topic):
            return {"a": 100, "b": 100}.get(topic, 0)

        slots = compute_topic_slots({"a": 0.5, "b": 0.5}, 2, count_fn)
        assert sum(slots.values()) == 2
