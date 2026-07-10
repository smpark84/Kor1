"""phase_classifier.py 단위 테스트. 각 국면 규칙 분기와 fallback(unclear)을 검증한다."""
import pandas as pd

from scripts.scoring.phase_classifier import classify_phase, classify_phase_row

_ALL_FALSE = dict(
    volume_surge=False,
    co_net_buy_active=False,
    is_bullish_alignment=False,
    is_ascending_pullback=False,
    credit_ratio_spike=False,
    credit_ratio_plunge=False,
    vi_trigger_frequent=False,
    distribution_flow_pattern=False,
)


def test_classify_phase_distribution():
    args = dict(_ALL_FALSE, distribution_flow_pattern=True, is_bullish_alignment=True)

    assert classify_phase(**args) == "distribution"


def test_classify_phase_markup():
    args = dict(_ALL_FALSE, volume_surge=True, vi_trigger_frequent=True, is_bullish_alignment=True)

    assert classify_phase(**args) == "markup"


def test_classify_phase_markdown():
    args = dict(_ALL_FALSE, credit_ratio_plunge=True, is_bullish_alignment=False)

    assert classify_phase(**args) == "markdown"


def test_classify_phase_accumulation():
    args = dict(
        _ALL_FALSE,
        is_ascending_pullback=True,
        co_net_buy_active=True,
        credit_ratio_spike=False,
    )

    assert classify_phase(**args) == "accumulation"


def test_classify_phase_unclear_when_no_pattern_matches():
    assert classify_phase(**_ALL_FALSE) == "unclear"


def test_classify_phase_row_wraps_series_correctly():
    row = pd.Series(dict(_ALL_FALSE, is_ascending_pullback=True, co_net_buy_active=True))

    assert classify_phase_row(row) == "accumulation"


def test_distribution_takes_priority_over_markup_when_both_partially_match():
    # 정배열 + 분산 플로우 패턴이 동시에 있으면 distribution이 markup보다 우선한다
    args = dict(
        _ALL_FALSE,
        is_bullish_alignment=True,
        distribution_flow_pattern=True,
        volume_surge=True,
        vi_trigger_frequent=True,
    )

    assert classify_phase(**args) == "distribution"
