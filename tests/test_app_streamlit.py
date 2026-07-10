"""app_streamlit.py의 순수 로직(화면 렌더링 제외)을 검증하는 단위 테스트."""
import pandas as pd

from scripts.dashboard.app_streamlit import (
    PHASE_LABELS_KO,
    classify_ticker_phase,
    load_screening_table,
)


def test_classify_ticker_phase_returns_known_label():
    from scripts.dashboard.app_streamlit import _make_demo_ticker_data

    df = _make_demo_ticker_data(seed=1, trend=1.2)

    phase = classify_ticker_phase(df)

    assert phase in {"accumulation", "markup", "distribution", "markdown", "unclear"}


def test_load_screening_table_has_expected_columns_and_is_sorted():
    table = load_screening_table()

    assert "세력_개입_의심_지수" in table.columns
    assert "국면_신호" in table.columns
    assert set(table["국면_신호"]).issubset(set(PHASE_LABELS_KO.values()))

    scores = table["세력_개입_의심_지수"]
    assert list(scores) == sorted(scores, reverse=True)
