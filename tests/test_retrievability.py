"""Tests for FSRS retrievability computation."""

import math
from datetime import datetime, timezone

import pytest

from agent.send_daily import compute_retrievability


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


class TestComputeRetrievability:
    def test_never_sent_returns_zero(self):
        assert compute_retrievability(3.0, 3.0, None, NOW) == 0.0

    def test_zero_stability_returns_zero(self):
        assert compute_retrievability(0.0, 3.0, "2026-07-10T00:00:00", NOW) == 0.0

    def test_negative_stability_returns_zero(self):
        assert compute_retrievability(-1.0, 3.0, "2026-07-10T00:00:00", NOW) == 0.0

    def test_same_day_returns_close_to_one(self):
        val = compute_retrievability(10.0, 3.0, "2026-07-16T08:00:00", NOW)
        assert val > 0.99

    def test_invalid_date_returns_zero(self):
        assert compute_retrievability(3.0, 3.0, "not-a-date", NOW) == 0.0

    def test_high_stability_decays_slower(self):
        high = compute_retrievability(100.0, 3.0, "2026-07-01T00:00:00", NOW)
        low = compute_retrievability(1.0, 3.0, "2026-07-01T00:00:00", NOW)
        assert high > low

    def test_fifteen_days_stability_20(self):
        val = compute_retrievability(20.0, 3.0, "2026-07-01T00:00:00", NOW)
        # R = 2^(-15/20) = 2^(-0.75) ≈ 0.5946
        expected = math.pow(2.0, -15.0 / 20.0)
        assert abs(val - expected) < 0.001

    def test_timezone_naive_conversion(self):
        val = compute_retrievability(5.0, 3.0, "2026-07-15T00:00:00", NOW)
        assert val > 0.0
        assert val < 1.0

    def test_past_date_is_clamped(self):
        val = compute_retrievability(5.0, 3.0, "2026-07-20T00:00:00", NOW)
        assert val >= 0.0
