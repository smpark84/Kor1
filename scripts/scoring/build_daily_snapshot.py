"""여러 종목의 시계열 데이터로부터 스코어링 입력 스냅샷을 조립하는 파이프라인.

indicator_*.py 모듈들은 종목 1개의 시계열(pd.Series)을 받아 시계열 결과를 반환하는
반면, scoring_engine.compute_score()는 "같은 시점, 여러 종목"을 비교하는 크로스섹션
DataFrame(행=종목, 열=지표 카테고리)을 기대한다. 이 모듈이 그 둘을 연결한다
(작업일지 2026-07-10 열린 이슈 5 해소).
"""
from __future__ import annotations

import pandas as pd

from scripts.indicators.indicator_credit_short import change_rate
from scripts.indicators.indicator_flow import co_net_buy_streak_days
from scripts.indicators.indicator_pattern import is_ascending_pullback, is_bullish_alignment
from scripts.indicators.indicator_vi import vi_like_trigger_count
from scripts.indicators.indicator_volume import volume_surge_ratio
from scripts.utils.config_loader import load_indicators_config

REQUIRED_COLUMNS = [
    "close", "high", "low", "volume",
    "institution_net", "foreign_net", "retail_net",
    "credit_ratio", "short_balance",
]


def build_ticker_features(ticker_df: pd.DataFrame) -> pd.Series:
    """종목 1개의 시계열 DataFrame에서 가장 최근 시점 기준 카테고리별 원시 피처를 계산.

    ticker_df는 날짜 오름차순 인덱스에 REQUIRED_COLUMNS를 포함해야 한다. 각 피처는
    "값이 클수록 세력 개입 의심이 커지는 방향"으로 정렬돼 scoring_engine에 바로 투입
    가능하다.
    """
    missing = set(REQUIRED_COLUMNS) - set(ticker_df.columns)
    if missing:
        raise ValueError(f"ticker_df에 필요한 컬럼이 없습니다: {missing}")

    cfg = load_indicators_config()

    volume_feature = volume_surge_ratio(ticker_df["volume"]).iloc[-1]

    flow_feature = co_net_buy_streak_days(
        ticker_df["institution_net"], ticker_df["foreign_net"]
    ).iloc[-1]

    credit_feature = change_rate(
        ticker_df["credit_ratio"], cfg["credit_short"]["credit_ratio_lookback_days"]
    ).iloc[-1]

    bullish = bool(is_bullish_alignment(ticker_df["close"]).iloc[-1])
    ascending = bool(is_ascending_pullback(ticker_df["low"]).iloc[-1])
    pattern_feature = float(bullish) + float(ascending)  # 0~2

    vi_feature = vi_like_trigger_count(
        ticker_df["high"], ticker_df["low"], ticker_df["close"]
    ).iloc[-1]

    return pd.Series(
        {
            "volume": volume_feature,
            "flow": flow_feature,
            "credit_short": credit_feature,
            "pattern": pattern_feature,
            "vi": vi_feature,
        }
    )


def build_daily_snapshot(ticker_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """{종목코드: 시계열 DataFrame} 딕셔너리를 스냅샷(행=종목, 열=카테고리) DataFrame으로 조립.

    반환값은 scoring_engine.compute_score()에 바로 넣을 수 있는 형태다.
    """
    rows = {ticker: build_ticker_features(df) for ticker, df in ticker_data.items()}
    return pd.DataFrame(rows).T
