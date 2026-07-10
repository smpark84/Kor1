"""indicator_vi.py 단위 테스트. 합성 데이터로 검증한다 (실제 VI 이벤트는 근사치이므로
발동 여부 자체가 아니라 함수 로직의 정확성을 검증하는 데 집중한다)."""
import pandas as pd

from scripts.indicators.indicator_vi import (
    is_dynamic_vi_like_move,
    is_static_vi_like_move,
    vi_like_trigger_count,
)


def _series(values: list[float]) -> pd.Series:
    idx = pd.date_range("2026-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=idx)


def test_is_static_vi_like_move_detects_large_close_change():
    # 2일차: +12% (임계 10% 초과), 3일차: 112->100 도 -10.7%로 임계 초과 (둘 다 트리거되는 게 정상)
    close = _series([100, 100, 112, 100])

    triggered = is_static_vi_like_move(close, threshold_pct=10.0)

    assert list(triggered.fillna(False)) == [False, False, True, True]


def test_is_dynamic_vi_like_move_detects_intraday_high_spike():
    close = _series([100, 100, 100, 100])
    high = _series([100, 100, 107, 100])  # 3일차 고가 +7% (임계 6% 초과)
    low = _series([100, 100, 100, 100])

    triggered = is_dynamic_vi_like_move(high, low, close, threshold_pct=6.0)

    assert list(triggered.fillna(False)) == [False, False, True, False]


def test_vi_like_trigger_count_accumulates_within_window():
    close = _series([100] * 10)
    # index0은 전일 종가가 없어 트리거 판정 불가 — index1, index4에 스파이크를 둔다.
    high = _series([100, 106, 100, 100, 106, 100, 100, 100, 100, 100])
    low = _series([100] * 10)

    count = vi_like_trigger_count(high, low, close, window_days=5, threshold_pct=6.0)

    # index4 시점 기준 최근 5일(0~4) 내 발동 2회(index1, index4)
    assert count.iloc[4] == 2.0
