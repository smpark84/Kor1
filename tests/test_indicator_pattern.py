"""indicator_pattern.py 단위 테스트. 합성 데이터로 검증한다."""
import pandas as pd

from scripts.indicators.indicator_pattern import is_ascending_pullback, is_bullish_alignment


def _series(values: list[float]) -> pd.Series:
    idx = pd.date_range("2026-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=idx)


def test_is_bullish_alignment_true_for_steady_uptrend():
    # 꾸준히 우상향하는 종가 → 짧은 이평선이 긴 이평선 위에 위치해야 함
    close = _series([100 + i for i in range(150)])

    aligned = is_bullish_alignment(close, periods=[5, 20, 60, 120])

    assert aligned.iloc[-1] == True  # noqa: E712


def test_is_bullish_alignment_false_for_downtrend():
    close = _series([250 - i for i in range(150)])

    aligned = is_bullish_alignment(close, periods=[5, 20, 60, 120])

    assert aligned.iloc[-1] == False  # noqa: E712


def test_is_ascending_pullback_detects_rising_lows():
    # 10일 구간 저점이 이전 10일 구간 저점보다 높아지는 패턴
    first_window = [100, 99, 98, 99, 100, 101, 102, 103, 104, 105]  # 최저 98
    second_window = [105, 104, 103, 102, 101, 105, 106, 107, 108, 109]  # 최저 101 (상승)
    low = _series(first_window + second_window)

    ascending = is_ascending_pullback(low, swing_window=10)

    assert ascending.iloc[-1] == True  # noqa: E712


def test_is_ascending_pullback_false_when_low_falls():
    first_window = [100] * 10  # 최저 100
    second_window = [90] * 10  # 최저 90 (하락)
    low = _series(first_window + second_window)

    ascending = is_ascending_pullback(low, swing_window=10)

    assert ascending.iloc[-1] == False  # noqa: E712
