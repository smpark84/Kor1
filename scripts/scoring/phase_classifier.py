"""국면(Phase) 규칙기반 분류기 — 1차 설계안 (백테스트 전 잠정).

와이코프(Wyckoff) 4국면 프레임(지침서 1.5)의 특징 조합을 규칙기반으로 근사 판정한다.
ML 기반 분류(로지스틱회귀 등)로의 전환은 백테스트로 유의미한 라벨 데이터가 쌓인 뒤
판단하기로 하고, 우선 규칙기반으로 구현한다 — 지침서 10장이 공시·뉴스 NLP에 대해
"1차 규칙기반 접근 우선 제안"이라 밝힌 것과 동일한 취지를 국면 분류에도 적용한 것
(2026-07-10 작업일지, 사용자가 진행 방향을 위임함에 따라 판단).

⚠️ 아래 조합 규칙과 임계값은 전부 1차 참고치이며, 6장 백테스트로 재검증 후 확정해야
한다. 이 분류 결과는 확정적 판단이 아니라 확률적 신호다. "~국면일 가능성이 높게
관측됨" 형태로만 해석·표시해야 한다 (2장, docs/legal_notice.md).
"""
from __future__ import annotations

from typing import Literal

import pandas as pd

Phase = Literal["accumulation", "markup", "distribution", "markdown", "unclear"]


def classify_phase(
    volume_surge: bool,
    co_net_buy_active: bool,
    is_bullish_alignment: bool,
    is_ascending_pullback: bool,
    credit_ratio_spike: bool,
    credit_ratio_plunge: bool,
    vi_trigger_frequent: bool,
    distribution_flow_pattern: bool,
) -> Phase:
    """단일 시점의 불리언 신호 조합으로 국면을 근사 판정한다 (지침서 1.5 표 참고).

    판정 우선순위(먼저 매칭되는 규칙을 채택):
    1. distribution — 정배열 상태에서 분산 플로우 패턴(개인 몰릴 때 기관/외국인 이탈) 관측
    2. markup — 거래량 급증 + VI 빈발 + 정배열 전환
    3. markdown — 신용잔고 급감(반대매매 추정) + 정배열 붕괴
    4. accumulation — 눌림목(저점 계단식 상승) + 동반 순매수 + 신용잔고 급증 없음
    5. unclear — 위 어느 조합에도 뚜렷이 해당하지 않음 (단독 지표 판단 금지 원칙, 1.4)
    """
    if distribution_flow_pattern and is_bullish_alignment:
        return "distribution"
    if volume_surge and vi_trigger_frequent and is_bullish_alignment:
        return "markup"
    if credit_ratio_plunge and not is_bullish_alignment:
        return "markdown"
    if is_ascending_pullback and co_net_buy_active and not credit_ratio_spike:
        return "accumulation"
    return "unclear"


def classify_phase_row(row: pd.Series) -> Phase:
    """DataFrame.apply(classify_phase_row, axis=1) 형태로 쓰기 위한 래퍼.

    row는 classify_phase의 파라미터명과 동일한 컬럼(volume_surge, co_net_buy_active,
    is_bullish_alignment, is_ascending_pullback, credit_ratio_spike, credit_ratio_plunge,
    vi_trigger_frequent, distribution_flow_pattern)을 가진 pd.Series여야 한다.
    """
    return classify_phase(
        volume_surge=bool(row["volume_surge"]),
        co_net_buy_active=bool(row["co_net_buy_active"]),
        is_bullish_alignment=bool(row["is_bullish_alignment"]),
        is_ascending_pullback=bool(row["is_ascending_pullback"]),
        credit_ratio_spike=bool(row["credit_ratio_spike"]),
        credit_ratio_plunge=bool(row["credit_ratio_plunge"]),
        vi_trigger_frequent=bool(row["vi_trigger_frequent"]),
        distribution_flow_pattern=bool(row["distribution_flow_pattern"]),
    )
