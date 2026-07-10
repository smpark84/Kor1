"""indicator_volume.py 단위 테스트. 네트워크 호출 없이 합성 데이터로 검증한다."""
import pandas as pd
import pytest

from scripts.indicators.indicator_volume import is_volume_surge, volume_surge_ratio


def _volume_series(values: list[float]) -> pd.Series:
    idx = pd.date_range("2026-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=idx, name="volume")


def test_volume_surge_ratio_basic():
    # 20일간 거래량 100 유지 후, 21일째 거래량 500 (5배 급증)
    values = [100.0] * 20 + [500.0]
    volume = _volume_series(values)

    ratio = volume_surge_ratio(volume, lookback_days=20)

    assert ratio.iloc[:20].isna().all()  # lookback 채워지기 전은 NaN
    assert ratio.iloc[20] == pytest.approx(5.0)


def test_volume_surge_ratio_excludes_current_day():
    # 급증 당일 거래량이 평균 계산에 섞이지 않는지 확인
    values = [100.0] * 20 + [1000.0, 1000.0]
    volume = _volume_series(values)

    ratio = volume_surge_ratio(volume, lookback_days=20)

    # 22번째 날(index 21) 시점엔 21번째 날의 1000이 평균에 포함되지만
    # 21번째 날(index 20) 시점엔 아직 100만 있어야 한다 (당일 제외).
    assert ratio.iloc[20] == pytest.approx(10.0)  # 1000 / 100
    assert ratio.iloc[21] < ratio.iloc[20]  # 평균에 1000이 섞여 희석됨


def test_is_volume_surge_threshold():
    values = [100.0] * 20 + [400.0]  # 4배 급증
    volume = _volume_series(values)

    surged = is_volume_surge(volume, lookback_days=20, threshold=3.0)
    not_surged = is_volume_surge(volume, lookback_days=20, threshold=5.0)

    assert surged.iloc[20] == True  # noqa: E712
    assert not_surged.iloc[20] == False  # noqa: E712
