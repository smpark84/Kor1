"""scoring_engine.py 단위 테스트. 합성 데이터로 검증한다."""
import numpy as np
import pandas as pd
import pytest

from scripts.scoring.scoring_engine import compute_score, percentile_rank_score


def test_percentile_rank_score_orders_correctly():
    raw = pd.Series([10, 30, 20], index=["A", "B", "C"])

    ranked = percentile_rank_score(raw)

    assert ranked["A"] < ranked["C"] < ranked["B"]
    assert ranked.max() == 100.0


def test_compute_score_equal_weights_matches_average_of_ranks():
    indicator_values = pd.DataFrame(
        {
            "volume": [10, 30, 20],
            "flow": [5, 5, 5],  # 동률 → 모두 같은 백분위
        },
        index=["A", "B", "C"],
    )
    weights = {"volume": 1.0, "flow": 1.0}

    score = compute_score(indicator_values, weights=weights)

    volume_rank = percentile_rank_score(indicator_values["volume"])
    flow_rank = percentile_rank_score(indicator_values["flow"])
    expected = (volume_rank + flow_rank) / 2

    pd.testing.assert_series_equal(score, expected, check_names=False)


def test_compute_score_ignores_missing_indicator_per_row():
    indicator_values = pd.DataFrame(
        {
            "volume": [10, 30, 20],
            "flow": [5, np.nan, 5],
        },
        index=["A", "B", "C"],
    )
    weights = {"volume": 1.0, "flow": 3.0}

    score = compute_score(indicator_values, weights=weights)

    # B는 flow가 결측이라 volume 랭크만으로 스코어가 산출돼야 함 (100점, 최댓값)
    volume_rank_b = percentile_rank_score(indicator_values["volume"])["B"]
    assert score["B"] == pytest.approx(volume_rank_b)


def test_compute_score_raises_on_unknown_weight_key():
    indicator_values = pd.DataFrame({"unknown_category": [1, 2, 3]})

    with pytest.raises(ValueError):
        compute_score(indicator_values, weights={"volume": 1.0})
