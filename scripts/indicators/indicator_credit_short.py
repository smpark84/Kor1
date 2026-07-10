"""신용잔고·공매도 지표 — MVP 우선 지표 3번: 신용융자잔고율 증가 추이.

신용거래융자잔고율 및 공매도 잔고 비중의 직전 N일 대비 상대 증가율. (지침서 1.4 (C))
급증 시 반대매매(강제청산) 리스크, 하락 베팅 증가 등의 참고 신호로 활용한다.
"""
from __future__ import annotations

import pandas as pd

from scripts.utils.config_loader import load_indicators_config


def change_rate(series: pd.Series, lookback_days: int) -> pd.Series:
    """직전 N일 대비 상대 증가율: (오늘값 - N일전값) / N일전값."""
    baseline = series.shift(lookback_days)
    return (series - baseline) / baseline


def is_credit_ratio_spike(
    credit_ratio: pd.Series,
    lookback_days: int | None = None,
    threshold: float | None = None,
) -> pd.Series:
    """신용융자잔고율 급증 여부. threshold 미지정 시 config의 credit_ratio_spike_pct 사용."""
    cfg = load_indicators_config()["credit_short"]
    if lookback_days is None:
        lookback_days = cfg["credit_ratio_lookback_days"]
    if threshold is None:
        threshold = cfg["credit_ratio_spike_pct"]

    return change_rate(credit_ratio, lookback_days) >= threshold


def is_short_balance_spike(
    short_balance: pd.Series,
    lookback_days: int | None = None,
    threshold: float | None = None,
) -> pd.Series:
    """공매도 잔고 급증 여부. threshold 미지정 시 config의 short_balance_spike_pct 사용."""
    cfg = load_indicators_config()["credit_short"]
    if lookback_days is None:
        lookback_days = cfg["short_balance_lookback_days"]
    if threshold is None:
        threshold = cfg["short_balance_spike_pct"]

    return change_rate(short_balance, lookback_days) >= threshold


def is_short_covering(
    short_balance: pd.Series,
    lookback_days: int | None = None,
    threshold: float | None = None,
) -> pd.Series:
    """공매도 잔고 감소(숏커버링) 여부 — 반등 신호 참고용. threshold는 음수 감소율 기준."""
    cfg = load_indicators_config()["credit_short"]
    if lookback_days is None:
        lookback_days = cfg["short_balance_lookback_days"]
    if threshold is None:
        threshold = -cfg["short_balance_spike_pct"]

    return change_rate(short_balance, lookback_days) <= threshold
