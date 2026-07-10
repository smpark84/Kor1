"""VI(변동성완화장치) 발동 이력 근사 지표 — MVP 우선 지표 5번.

⚠️ 근사치 주의: 실제 VI 발동 이력(동적/정적, 발동 시각·횟수)은 KRX의 장중 이벤트 로그가
필요하지만, Phase 1(EOD 배치) 단계에서는 해당 데이터가 없다. 이 모듈은 일별 시가/고가/
저가/종가만으로 "VI가 발동했을 가능성이 높은 날"을 근사 추정하는 1차 대체 지표이며,
실제 VI 발동 이력과 정확히 일치하지 않을 수 있다. 실제 이력 연동은 Phase 2(실시간/장중
데이터 수집) 이후 과제로 남긴다 (지침서 1.4 (E), 작업일지 참고).
"""
from __future__ import annotations

import pandas as pd

from scripts.utils.config_loader import load_indicators_config


def is_static_vi_like_move(close: pd.Series, threshold_pct: float | None = None) -> pd.Series:
    """정적 VI 근사: 전일 종가 대비 |변동률|이 threshold_pct 이상인 날."""
    if threshold_pct is None:
        threshold_pct = load_indicators_config()["vi"]["static_pct"]

    prev_close = close.shift(1)
    change_pct = (close - prev_close).abs() / prev_close * 100
    return change_pct >= threshold_pct


def is_dynamic_vi_like_move(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    threshold_pct: float | None = None,
) -> pd.Series:
    """동적 VI 근사: 장중 고가/저가가 전일 종가 대비 threshold_pct 이상 괴리된 날.

    threshold_pct 미지정 시 config의 vi.dynamic_others_kosdaq_pct(6%)를 기본값으로 사용한다.
    코스피200 종목(3% 기준)은 호출 시 threshold_pct=config["vi"]["dynamic_kospi200_pct"]로
    명시적으로 넘겨야 한다.
    """
    if threshold_pct is None:
        threshold_pct = load_indicators_config()["vi"]["dynamic_others_kosdaq_pct"]

    prev_close = close.shift(1)
    up_move = (high - prev_close) / prev_close * 100
    down_move = (prev_close - low) / prev_close * 100
    return (up_move >= threshold_pct) | (down_move >= threshold_pct)


def vi_like_trigger_count(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window_days: int | None = None,
    threshold_pct: float | None = None,
) -> pd.Series:
    """최근 window_days 동안의 VI-근사 발동(동적 기준) 횟수. 발동 빈도 급증 탐지용."""
    cfg = load_indicators_config()["vi"]
    if window_days is None:
        window_days = cfg["lookback_months"] * 21  # 월 평균 거래일수 근사(21일)

    triggers = is_dynamic_vi_like_move(high, low, close, threshold_pct)
    return triggers.rolling(window=window_days, min_periods=1).sum()
