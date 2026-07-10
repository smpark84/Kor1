"""캔들/이동평균선 패턴 지표 — MVP 우선 지표 4번: 정배열 전환 + 눌림목.

정배열(5>20>60>120일선) 전환과 눌림목(저점 계단식 상승) 패턴. (지침서 1.4 (F))
눌림목 판정은 지역 저점(swing low)을 rolling min으로 근사한 것으로, 노이즈가 커서
단독 사용을 금지하고 다른 지표와 조합해야 한다는 지침서 지적을 그대로 따른다.
"""
from __future__ import annotations

import pandas as pd

from scripts.utils.config_loader import load_indicators_config


def moving_averages(close: pd.Series, periods: list[int] | None = None) -> pd.DataFrame:
    """periods별 단순 이동평균 DataFrame. periods 미지정 시 config의 pattern.ma_periods 사용."""
    if periods is None:
        periods = load_indicators_config()["pattern"]["ma_periods"]
    return pd.DataFrame({f"ma{p}": close.rolling(window=p, min_periods=p).mean() for p in periods})


def is_bullish_alignment(close: pd.Series, periods: list[int] | None = None) -> pd.Series:
    """정배열 여부: 짧은 기간 이평선이 긴 기간 이평선보다 모두 위에 있는가."""
    if periods is None:
        periods = load_indicators_config()["pattern"]["ma_periods"]
    sorted_periods = sorted(periods)

    mas = moving_averages(close, sorted_periods)
    aligned = pd.Series(True, index=close.index)
    for shorter, longer in zip(sorted_periods, sorted_periods[1:]):
        aligned &= mas[f"ma{shorter}"] > mas[f"ma{longer}"]
    return aligned


def swing_lows(low: pd.Series, window: int) -> pd.Series:
    """window 구간 내 최저가(지역 저점의 근사치)."""
    return low.rolling(window=window, min_periods=window).min()


def is_ascending_pullback(low: pd.Series, swing_window: int | None = None) -> pd.Series:
    """눌림목(저점 계단식 상승) 근사 판정.

    직전 swing_window 구간의 최저가가, 그 이전 동일 길이 구간의 최저가보다 높으면
    저점이 올라가고 있는 것으로 본다. swing_window 미지정 시 config의
    pattern.pullback_lookback_days // 6 (기본 60일 → 10일 단위 구간) 사용.
    """
    if swing_window is None:
        lookback = load_indicators_config()["pattern"]["pullback_lookback_days"]
        swing_window = max(lookback // 6, 1)

    recent_low = swing_lows(low, swing_window)
    prior_low = recent_low.shift(swing_window)
    return recent_low > prior_low
