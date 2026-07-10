"""거래량 기반 지표 — MVP 우선 지표 1번: 거래량 급증률.

당일(또는 특정 봉) 거래량 ÷ 직전 N일 평균 거래량. (지침서 1.4 (A))
N일/배수 임계값은 config/indicators_config.yaml 의 잠정치이며, 6장 백테스트로
재검증 후 확정한다. 이 모듈은 순수 계산 로직만 담당하며 데이터 수집(collectors)이나
스코어링(scoring)에 의존하지 않는다 (4장 설계 원칙: 모듈 독립).
"""
from __future__ import annotations

import pandas as pd

from scripts.utils.config_loader import load_indicators_config


def volume_surge_ratio(volume: pd.Series, lookback_days: int | None = None) -> pd.Series:
    """당일 거래량 / 직전 N일(당일 제외) 평균 거래량.

    당일을 평균 계산에서 제외해 자기 자신이 비율을 왜곡하지 않도록 한다
    (lookahead bias 방지 원칙, 지침서 6.2와 동일한 취지).
    """
    if lookback_days is None:
        lookback_days = load_indicators_config()["volume"]["surge_lookback_days"]

    prior_avg = volume.shift(1).rolling(window=lookback_days, min_periods=lookback_days).mean()
    return volume / prior_avg


def is_volume_surge(
    volume: pd.Series,
    lookback_days: int | None = None,
    threshold: float | None = None,
) -> pd.Series:
    """거래량 급증 여부(불리언 시리즈). threshold 미지정 시 config 값을 사용."""
    cfg = load_indicators_config()["volume"]
    if lookback_days is None:
        lookback_days = cfg["surge_lookback_days"]
    if threshold is None:
        threshold = cfg["surge_ratio_threshold"]

    ratio = volume_surge_ratio(volume, lookback_days)
    return ratio >= threshold
