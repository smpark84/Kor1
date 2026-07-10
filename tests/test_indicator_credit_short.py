"""indicator_credit_short.py 단위 테스트. 합성 데이터로 검증한다."""
import pandas as pd

from scripts.indicators.indicator_credit_short import (
    change_rate,
    is_credit_ratio_spike,
    is_short_balance_spike,
    is_short_covering,
)


def _series(values: list[float]) -> pd.Series:
    idx = pd.date_range("2026-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=idx)


def test_change_rate_basic():
    values = [100.0] * 5 + [150.0]  # 5일 전 대비 50% 증가
    series = _series(values)

    rate = change_rate(series, lookback_days=5)

    assert rate.iloc[5] == 0.5


def test_is_credit_ratio_spike():
    values = [10.0] * 20 + [14.0]  # 20일 전 대비 40% 증가
    credit_ratio = _series(values)

    spiked = is_credit_ratio_spike(credit_ratio, lookback_days=20, threshold=0.3)
    not_spiked = is_credit_ratio_spike(credit_ratio, lookback_days=20, threshold=0.5)

    assert spiked.iloc[20] == True  # noqa: E712
    assert not_spiked.iloc[20] == False  # noqa: E712


def test_short_balance_spike_and_covering_are_opposite_directions():
    values = [100.0] * 20 + [140.0]  # 급증
    short_balance = _series(values)

    assert is_short_balance_spike(short_balance, lookback_days=20, threshold=0.3).iloc[20]
    assert not is_short_covering(short_balance, lookback_days=20, threshold=-0.3).iloc[20]

    covering_values = [100.0] * 20 + [60.0]  # 급감 (숏커버링)
    covering_balance = _series(covering_values)

    assert is_short_covering(covering_balance, lookback_days=20, threshold=-0.3).iloc[20]
    assert not is_short_balance_spike(covering_balance, lookback_days=20, threshold=0.3).iloc[20]
