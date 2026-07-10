"""collector_credit_short.py 단위 테스트. 신용잔고는 의도적 미구현 상태이므로 그 계약만
확인한다 (실제 pykrx 공매도 잔고 API 호출은 이 환경의 네트워크 제약으로 검증 불가)."""
import pytest

from scripts.collectors.collector_credit_short import get_credit_balance


def test_get_credit_balance_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="FreeSIS"):
        get_credit_balance("005930", "20260101", "20260110")
