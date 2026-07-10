"""collector_dart.py 단위 테스트. 네트워크 호출 없이 키 검증 로직만 확인한다
(실제 DART API 호출은 이 환경의 네트워크 제약으로 검증 불가 — 작업일지 참고)."""
import pytest

from scripts.collectors.collector_dart import _get_client


def test_get_client_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("DART_API_KEY", raising=False)

    with pytest.raises(ValueError, match="DART_API_KEY"):
        _get_client(api_key=None)


def test_get_client_accepts_explicit_api_key_without_network_call(monkeypatch):
    # OpenDartReader 생성자가 실제로 네트워크를 호출하지 않는지까지는 라이브러리 내부
    # 구현에 달려있어 이 환경에서 완전히 검증할 수 없다. 여기서는 명시적 키가 주어졌을 때
    # ValueError(키 누락)가 발생하지 않는 것만 확인한다.
    try:
        _get_client(api_key="dummy_key_for_test")
    except ValueError as e:
        pytest.fail(f"명시적 키를 줬는데도 ValueError 발생: {e}")
    except Exception:
        # 네트워크/인증 관련 다른 예외는 이 환경 제약상 발생할 수 있어 허용한다.
        pass
