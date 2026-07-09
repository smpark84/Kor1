# 데이터 소스 명세

> 출처: 지침서(`docs/project_spec.md`) 3장.

## 소스 후보

| 구분 | 소스 | 제공 정보 | 비용 | 접근 난이도 | 형태 |
|---|---|---|---|---|---|
| 공식 | KRX 정보데이터시스템 (data.krx.co.kr) | 시세, 투자자별 매매동향, 공매도 잔고 등 | 무료 | 중 | Excel/CSV, 웹 |
| 공식 | KRX Data Marketplace Open API | 시장 정보, 파생상품, 공매도 통합 API | 무료/일부 유료 | 중 (신청 필요) | REST API |
| 공식 | 전자공시 OPEN DART | 공시원문, 재무제표, 지분보고서 | 무료 (키 발급) | 중 | REST API |
| 공식 | 공공데이터포털 KRX상장종목정보 | 상장종목 기본정보 | 무료 (키 발급) | 낮음 | REST API |
| 공식 | 금융투자협회 FreeSIS | 신용거래융자잔고 통계 | 무료 | 낮~중 | 웹 조회/다운로드 |
| 증권사 API | 한국투자증권 KIS Developers | 실시간 시세/호가/체결, 계좌조회(조회 목적만 사용) | 무료 (계좌 필요) | 중~높 | REST/WebSocket |
| 증권사 API | 키움증권 Open API+ | 실시간 시세, 조건검색, 수급 | 무료 (계좌+신청) | 높음 (Windows COM/OCX) | OCX/COM |
| 라이브러리 | pykrx | KRX+네이버 스크래핑 기반 시세/재무/공매도 | 무료 | 낮음 | Python 라이브러리 |
| 라이브러리 | FinanceDataReader | 종목코드, 기본 시세 | 무료 | 낮음 | Python 라이브러리 |
| 라이브러리 | OpenDartReader / dart-fss | DART API 래퍼 | 무료 (DART 키 필요) | 낮음 | Python 라이브러리 |
| 참고용 | 네이버금융/다음금융 | 시세, 투자자별 매매동향, 뉴스 | 무료 (비공식) | 낮음 (ToS·구조변경 리스크) | HTML 스크래핑 |
| 참고용 | 한경컨센서스 등 | 애널리스트 리포트, 목표주가 | 무료 | 낮음 | PDF/HTML |
| 참고용(유료) | 퀀트킹, 퀀터스 | 팩터 스크리닝, 백테스트 UI | 유료 | 낮음 (SaaS) | 웹 서비스 |

## 권장 우선순위 (MVP 기준)

```
pykrx + FinanceDataReader (시세/기본 데이터)
    → DART Open API (공시)
    → KRX 정보데이터시스템 (투자자별 매매동향, 신용잔고, 공매도)
    → 한국투자증권 KIS API (실시간 호가/체결, Phase 2+)

키움 Open API+ 는 Windows COM 의존성이 커서 Phase 3+ 선택 사항.
```

## Collector 모듈 매핑

| 파일 | 담당 소스 | 상태 |
|---|---|---|
| `scripts/collectors/collector_krx.py` | pykrx (OHLCV, 투자자별 매매동향, 공매도) | 프로토타입 작성 중 (작업일지 참고) |
| `scripts/collectors/collector_dart.py` | DART Open API (공시) | 미착수 |
| `scripts/collectors/collector_credit_short.py` | FreeSIS/KRX 신용잔고·공매도 잔고 | 미착수 |
| `scripts/collectors/collector_realtime.py` | KIS WebSocket (호가/체결/VI) | Phase 2+, 미착수 |

## 이용약관/레이트리밋 주의사항 (2.6 원칙)

- 각 소스의 요청 빈도 제한을 준수하고, 배치 수집 시 요청 간 지연(sleep)을 둔다.
- 스크래핑 기반 소스(네이버/다음, pykrx 일부)는 구조 변경 시 깨질 수 있으므로 예외처리
  필수 (10장 리스크 참고).
- DART API는 키 발급 후 일일 요청 한도가 있으므로 캐싱을 적극 활용한다(`data/cache/`).
