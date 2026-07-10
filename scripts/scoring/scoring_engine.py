"""세력 개입 의심 지수 스코어링 엔진.

각 지표 카테고리의 원시 신호값을 유니버스 내 백분위 랭크(0~100)로 정규화한 뒤,
config/indicators_config.yaml의 weights로 가중합해 "세력 개입 의심 지수(0~100)"를
산출한다 (지침서 1.5 1차 설계안: "정규화 후 가중합"). 가중치는 백테스트 전 잠정
균등값이며, 6장 백테스트로 재검증 후 확정한다.

⚠️ 이 스코어는 확정적 판단이 아니라 확률적 신호다 (지침서 2장). 소비하는 쪽(대시보드,
알림, 리포트)은 "세력주다"가 아니라 "세력 개입 의심 지수 XX/100 — 특정 국면 신호
관측"처럼 확률적으로만 표현해야 한다 (docs/legal_notice.md 참고).
"""
from __future__ import annotations

import pandas as pd

from scripts.utils.config_loader import load_indicators_config


def percentile_rank_score(raw: pd.Series) -> pd.Series:
    """원시 지표값을 유니버스 내 백분위 랭크(0~100)로 정규화.

    raw는 "값이 클수록 세력 개입 의심이 커지는 방향"으로 이미 정렬돼 있어야 한다
    (예: 거래량 급증률, 순매수 연속일수 등). 같은 시점 여러 종목을 비교하는 크로스섹션
    시리즈를 가정한다.
    """
    return raw.rank(pct=True, na_option="keep") * 100


def compute_score(indicator_values: pd.DataFrame, weights: dict[str, float] | None = None) -> pd.Series:
    """카테고리별 원시 지표값(컬럼=카테고리명, 행=종목)을 받아 가중합 스코어(0~100)를 산출.

    결측(NaN)이 있는 지표는 해당 종목의 스코어 계산에서 제외하고, 실제로 값이 있는
    지표들의 가중치 비율로 재정규화한다(전부 결측이면 결과도 결측).
    """
    if weights is None:
        weights = load_indicators_config()["scoring"]["weights"]

    missing = set(indicator_values.columns) - set(weights)
    if missing:
        raise ValueError(f"weights에 없는 지표 카테고리: {missing}")

    normalized = indicator_values.apply(percentile_rank_score)
    weight_series = pd.Series({col: weights[col] for col in normalized.columns})

    weighted_sum = normalized.mul(weight_series, axis=1).sum(axis=1, skipna=True)
    active_weight = normalized.notna().mul(weight_series, axis=1).sum(axis=1)

    score = weighted_sum / active_weight
    return score.where(active_weight > 0)
