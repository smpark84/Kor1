"""build_daily_snapshot.py 단위 테스트. 합성 데이터로 검증한다."""
import numpy as np
import pandas as pd
import pytest

from scripts.scoring.build_daily_snapshot import build_daily_snapshot, build_ticker_features
from scripts.scoring.scoring_engine import compute_score


def _make_ticker_df(n: int = 130, trend: float = 1.0, seed: int = 0) -> pd.DataFrame:
    idx = pd.date_range("2026-01-01", periods=n, freq="D")
    rng = np.random.default_rng(seed)
    close = 100 + trend * pd.Series(range(n), index=idx) + rng.normal(0, 0.1, n)
    high = close + 0.5
    low = close - 0.5

    volume = pd.Series(100.0, index=idx)
    volume.iloc[-1] = 500.0  # 마지막날 거래량 급증(5배)

    institution_net = pd.Series(1.0, index=idx)
    foreign_net = pd.Series(1.0, index=idx)
    retail_net = pd.Series(-2.0, index=idx)

    credit_ratio = pd.Series(10.0, index=idx)
    credit_ratio.iloc[-1] = 13.0  # 20일 전 대비 +30%

    short_balance = pd.Series(5.0, index=idx)

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


def test_build_ticker_features_returns_expected_categories_and_values():
    df = _make_ticker_df()

    features = build_ticker_features(df)

    assert set(features.index) == {"volume", "flow", "credit_short", "pattern", "vi"}
    assert features["volume"] == pytest.approx(5.0)
    assert features["flow"] == 130  # 전 기간 기관+외국인 동반 순매수
    assert features["credit_short"] == pytest.approx(0.3)
    assert features["pattern"] in (0.0, 1.0, 2.0)
    assert features["vi"] >= 0


def test_build_ticker_features_raises_on_missing_column():
    df = _make_ticker_df().drop(columns=["volume"])

    with pytest.raises(ValueError):
        build_ticker_features(df)


def test_build_daily_snapshot_combines_multiple_tickers():
    data = {
        "005930": _make_ticker_df(seed=1, trend=1.0),
        "000660": _make_ticker_df(seed=2, trend=-1.0),
    }

    snapshot = build_daily_snapshot(data)

    assert list(snapshot.index) == ["005930", "000660"]
    assert set(snapshot.columns) == {"volume", "flow", "credit_short", "pattern", "vi"}


def test_snapshot_feeds_into_scoring_engine():
    data = {
        "A": _make_ticker_df(seed=1, trend=1.0),
        "B": _make_ticker_df(seed=2, trend=-1.0),
    }
    snapshot = build_daily_snapshot(data)
    weights = {"volume": 1.0, "flow": 1.0, "credit_short": 1.0, "pattern": 1.0, "vi": 1.0}

    score = compute_score(snapshot, weights=weights)

    assert set(score.index) == {"A", "B"}
    assert ((score >= 0) & (score <= 100)).all()
