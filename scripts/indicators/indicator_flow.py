"""수급주체별 매매동향 지표 — MVP 우선 지표 2번: 기관+외국인 동반 순매수.

기관+외국인 동반 순매수 연속일수 및 해당 연속 구간의 누적 순매수 대금. (지침서 1.4 (B))
개인 급증×기관/외국인 순매도 동시발생(분산 국면 신호)도 함께 제공한다.
입력은 종목별 일별 순매수 금액 시리즈(pd.Series)로, 수집기(collector) 구현과 무관하게
독립적으로 동작한다 (4장 설계 원칙).
"""
from __future__ import annotations

import pandas as pd


def _run_id(flag: pd.Series) -> pd.Series:
    """flag 값이 이전 행과 달라질 때마다 증가하는 그룹 id (연속 True/False 구간 구분용)."""
    return (flag != flag.shift()).cumsum()


def co_net_buy_streak_days(institution_net: pd.Series, foreign_net: pd.Series) -> pd.Series:
    """기관+외국인 동반 순매수 연속일수. 연속이 끊기면 0으로 리셋된다."""
    co_buy = (institution_net > 0) & (foreign_net > 0)
    streak = co_buy.groupby(_run_id(co_buy)).cumcount() + 1
    return streak.where(co_buy, 0)


def co_net_buy_cumulative_amount(institution_net: pd.Series, foreign_net: pd.Series) -> pd.Series:
    """현재 진행 중인 동반 순매수 연속 구간의 누적 순매수 대금(기관+외국인 합산)."""
    co_buy = (institution_net > 0) & (foreign_net > 0)
    combined = institution_net + foreign_net
    cum_amount = combined.where(co_buy, 0.0).groupby(_run_id(co_buy)).cumsum()
    return cum_amount.where(co_buy, 0.0)


def is_distribution_flow_pattern(
    institution_net: pd.Series,
    foreign_net: pd.Series,
    retail_net: pd.Series,
) -> pd.Series:
    """개인 순매수 급증과 기관/외국인 순매도 전환의 동시 발생 (분산 국면 신호).

    개인이 순매수(>0)인 동시에 기관과 외국인이 모두 순매도(<0)인 날을 표시한다.
    """
    return (retail_net > 0) & (institution_net < 0) & (foreign_net < 0)
