"""indicator_flow.py 단위 테스트. 합성 데이터로 검증한다."""
import pandas as pd

from scripts.indicators.indicator_flow import (
    co_net_buy_cumulative_amount,
    co_net_buy_streak_days,
    is_distribution_flow_pattern,
)


def _series(values: list[float]) -> pd.Series:
    idx = pd.date_range("2026-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=idx)


def test_co_net_buy_streak_days_resets_on_break():
    institution = _series([10, 10, -5, 10, 10, 10])
    foreign = _series([5, 5, 5, 5, 5, 5])

    streak = co_net_buy_streak_days(institution, foreign)

    assert list(streak) == [1, 2, 0, 1, 2, 3]


def test_co_net_buy_cumulative_amount_resets_and_sums():
    institution = _series([10, 10, -5, 10, 10])
    foreign = _series([5, 5, 5, 5, 5])

    cum = co_net_buy_cumulative_amount(institution, foreign)

    # 1~2일차: (10+5)+(10+5)=30, 3일차: 끊김(0), 4~5일차: 15, 30
    assert list(cum) == [15.0, 30.0, 0.0, 15.0, 30.0]


def test_is_distribution_flow_pattern():
    institution = _series([-10, 10, -10])
    foreign = _series([-5, -5, -5])
    retail = _series([20, 20, -5])

    result = is_distribution_flow_pattern(institution, foreign, retail)

    assert list(result) == [True, False, False]
