"""Phase 1 MVP 배치 스크리너 대시보드 (Streamlit).

지표(indicator_*.py) → 스냅샷 조립(build_daily_snapshot) → 스코어링(scoring_engine) →
국면 분류(phase_classifier)까지의 1차 파이프라인을 화면으로 확인할 수 있는 최소 대시보드.

⚠️ 투자 자문 아님: 본 화면의 모든 수치는 투자 참고용 확률적 신호이며 매매 추천이 아니다
(지침서 2장, docs/legal_notice.md). "세력주다/사라/팔아라" 같은 단정적 표현을 쓰지 않는다.

⚠️ 데모 모드: 이 코드를 작성한 실행 환경은 네트워크 정책상 KRX 등 외부 데이터 소스에
접근할 수 없어(project_작업일지.md 참고), 실제 시세 대신 샘플 데이터로 화면 구조만 보여준다.
실제 데이터 연동은 scripts/collectors/*.py를 네트워크 제약 없는 환경에서 실행해 그 결과를
load_screening_table()에 연결하면 된다.

실행: streamlit run scripts/dashboard/app_streamlit.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from scripts.indicators.indicator_credit_short import change_rate, is_credit_ratio_spike
from scripts.indicators.indicator_flow import co_net_buy_streak_days, is_distribution_flow_pattern
from scripts.indicators.indicator_pattern import is_ascending_pullback, is_bullish_alignment
from scripts.indicators.indicator_vi import vi_like_trigger_count
from scripts.indicators.indicator_volume import is_volume_surge
from scripts.scoring.build_daily_snapshot import build_daily_snapshot
from scripts.scoring.phase_classifier import classify_phase
from scripts.scoring.scoring_engine import compute_score
from scripts.utils.config_loader import load_indicators_config

DISCLAIMER = (
    "⚠️ 본 정보는 투자 참고용으로만 제공되며, 투자 자문이나 매매 추천이 아닙니다. "
    "투자 판단과 그에 따른 책임은 전적으로 이용자 본인에게 있습니다. 본 스코어링은 "
    "과거 데이터 패턴에 기반한 확률적 추정이며, 실제 세력 개입 여부를 보장하지 않습니다(오탐 가능)."
)

PHASE_LABELS_KO = {
    "accumulation": "매집 국면 신호 관측",
    "markup": "상승 국면 신호 관측",
    "distribution": "분산 국면 신호 관측",
    "markdown": "하락 국면 신호 관측",
    "unclear": "국면 신호 불명확",
}


def _make_demo_ticker_data(seed: int, trend: float, n: int = 130) -> pd.DataFrame:
    """실데이터 수집이 불가능한 환경에서 화면 구조 확인용 샘플 데이터를 생성한다.

    ⚠️ 실제 시세가 아니다. 데모/구조 확인 목적으로만 사용한다.
    """
    idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq="B")
    rng = np.random.default_rng(seed)

    close = 100 + trend * pd.Series(range(n), index=idx) + rng.normal(0, 1.0, n)
    high = close + rng.uniform(0, 2, n)
    low = close - rng.uniform(0, 2, n)

    volume = pd.Series(rng.uniform(80, 120, n), index=idx)
    volume.iloc[-1] *= rng.uniform(2, 6)  # 마지막 날 거래량 급증 연출

    institution_net = pd.Series(rng.normal(1, 3, n), index=idx)
    foreign_net = pd.Series(rng.normal(1, 3, n), index=idx)
    retail_net = -(institution_net + foreign_net) + rng.normal(0, 1, n)

    credit_ratio = pd.Series(10 + rng.normal(0, 0.3, n).cumsum() * 0.05, index=idx)
    short_balance = pd.Series(5 + rng.normal(0, 0.2, n).cumsum() * 0.05, index=idx)

    return pd.DataFrame(
        {
            "close": close,
            "high": high,
            "low": low,
            "volume": volume,
            "institution_net": institution_net,
            "foreign_net": foreign_net,
            "retail_net": retail_net,
            "credit_ratio": credit_ratio,
            "short_balance": short_balance,
        }
    )


def classify_ticker_phase(df: pd.DataFrame) -> str:
    """종목 1개의 시계열 DataFrame에서 국면 분류에 필요한 불리언 신호를 뽑아 classify_phase 호출."""
    cfg = load_indicators_config()

    volume_surge = bool(is_volume_surge(df["volume"]).iloc[-1])
    co_net_buy_active = bool(
        co_net_buy_streak_days(df["institution_net"], df["foreign_net"]).iloc[-1] > 0
    )
    bullish = bool(is_bullish_alignment(df["close"]).iloc[-1])
    ascending = bool(is_ascending_pullback(df["low"]).iloc[-1])
    credit_spike = bool(is_credit_ratio_spike(df["credit_ratio"]).iloc[-1])

    credit_change = change_rate(
        df["credit_ratio"], cfg["credit_short"]["credit_ratio_lookback_days"]
    ).iloc[-1]
    credit_plunge = bool(
        pd.notna(credit_change) and credit_change <= -cfg["credit_short"]["credit_ratio_spike_pct"]
    )

    vi_count = vi_like_trigger_count(df["high"], df["low"], df["close"]).iloc[-1]
    vi_frequent = bool(pd.notna(vi_count) and vi_count >= 3)

    distribution_pattern = bool(
        is_distribution_flow_pattern(df["institution_net"], df["foreign_net"], df["retail_net"]).iloc[-1]
    )

    return classify_phase(
        volume_surge=volume_surge,
        co_net_buy_active=co_net_buy_active,
        is_bullish_alignment=bullish,
        is_ascending_pullback=ascending,
        credit_ratio_spike=credit_spike,
        credit_ratio_plunge=credit_plunge,
        vi_trigger_frequent=vi_frequent,
        distribution_flow_pattern=distribution_pattern,
    )


def load_screening_table() -> pd.DataFrame:
    """데모 유니버스에 전체 파이프라인(지표→스냅샷→스코어→국면)을 적용해 스크리닝 테이블을 만든다."""
    demo_universe = {
        "005930 (데모)": _make_demo_ticker_data(seed=1, trend=1.2),
        "000660 (데모)": _make_demo_ticker_data(seed=2, trend=-0.8),
        "035420 (데모)": _make_demo_ticker_data(seed=3, trend=0.1),
        "247540 (데모)": _make_demo_ticker_data(seed=4, trend=2.0),
    }

    snapshot = build_daily_snapshot(demo_universe)
    weights = load_indicators_config()["scoring"]["weights"]
    score = compute_score(snapshot, weights=weights)

    phases = {ticker: classify_ticker_phase(df) for ticker, df in demo_universe.items()}

    table = snapshot.copy()
    table["세력_개입_의심_지수"] = score.round(1)
    table["국면_신호"] = pd.Series(phases).map(PHASE_LABELS_KO)
    return table.sort_values("세력_개입_의심_지수", ascending=False)


def main() -> None:
    st.set_page_config(page_title="세력주 탐지 스크리너 (MVP)", layout="wide")
    st.title("세력주 탐지 및 매매 국면 추정 — 배치 스크리너 (Phase 1 MVP)")

    st.warning(
        "⚠️ 데모 모드: 이 화면은 실제 시세가 아닌 샘플 데이터로 파이프라인 구조를 보여줍니다. "
        "실제 데이터 연동은 scripts/collectors/*.py 실행 결과를 연결해야 합니다."
    )

    table = load_screening_table()
    st.dataframe(table, use_container_width=True)

    st.caption(DISCLAIMER)


if __name__ == "__main__":
    main()
