# 아키텍처

> 출처: 지침서(`docs/project_spec.md`) 4장. 이 문서는 파이프라인 단계별 모듈 책임과
> 저장소 내 실제 파일 매핑을 정리한다.

## 파이프라인 개요

```
[1] 수집(Collectors)  →  [2] 저장(Storage)  →  [3] 지표(Indicators)
        →  [4] 스코어링(Scoring)  →  [5] 산출(Output: 대시보드/알림/리포트)

[별도 트랙] 백테스트(Backtest) — 과거 데이터로 [3][4] 로직을 검증
```

## 모듈 ↔ 파일 매핑

| 단계 | 책임 | 저장소 경로 | Phase |
|---|---|---|---|
| 수집(배치) | 일별 시세, 투자자별 매매동향, 신용잔고, 공매도, 공시 목록 | `scripts/collectors/collector_krx.py`, `collector_dart.py`, `collector_credit_short.py` | 1 |
| 수집(실시간) | 호가/체결/VI 발동 이벤트 | `scripts/collectors/collector_realtime.py` | 2+ |
| 저장 | 원시(raw)/정제(processed) 데이터 | `data/raw/`, `data/processed/` (SQLite/DuckDB, MVP는 별도 DB 서버 불필요) | 1 |
| 지표 | 카테고리별 지표 계산 | `scripts/indicators/indicator_volume.py`, `indicator_flow.py`, `indicator_credit_short.py`, `indicator_orderbook.py`, `indicator_vi.py`, `indicator_pattern.py` | 1~2 |
| 스코어링 | 세력 개입 의심 지수 + 국면 분류 | `scripts/scoring/scoring_engine.py`, `phase_classifier.py` | 1 |
| 백테스트 | 과거 데이터 검증 | `scripts/backtest/backtest_runner.py`, `backtest_metrics.py` | 1 |
| 대시보드 | 스크리닝 테이블 + 종목 상세 | `scripts/dashboard/app_streamlit.py` | 1 |
| 알림 | 텔레그램 정보 통지 (주문 아님) | `scripts/alerts/telegram_bot.py` | 3 |
| 공통 | 로거, 설정 로더 | `scripts/utils/logger.py`, `config_loader.py` | 1 |

## 설계 원칙

- 수집 / 지표 / 스코어링 / 출력은 서로 독립 모듈로 분리 — 재사용성·테스트 용이성 확보.
- 배치(일 단위) 파이프라인을 먼저 안정화한 뒤 실시간 요소를 단계적으로 추가 (5장 로드맵).
- 공시 데이터는 반드시 "발표 시각" 기준 시점 정합성 유지 — 사후 확정 정보를 과거 시점
  분석에 사용하지 않는다(lookahead bias 금지, 6장 백테스트에서 특히 중요).
- 파일 하나가 18KB를 넘을 것으로 예상되면 설계 단계에서 미리 책임 단위로 분할한다
  (지침서 8.2). 함수/클래스가 300~400줄을 넘으면 하위 모듈로 추출.

## Phase 로드맵 (5장)

| Phase | 산출물 | 비고 |
|---|---|---|
| 1 (MVP) | 배치 스크리너 + Streamlit 정적 대시보드 | EOD 데이터, 실시간 인프라 불필요 |
| 2 | 준실시간 대시보드 (1~5분 폴링) | 웹소켓 없이 체감 지연 축소 |
| 3 | 텔레그램 알림 봇 | 임계값 돌파/국면 전환 통지 |
| 4 | 실시간 대시보드 (WebSocket) | 인프라 복잡도 큼, 1~3 안정화 후 판단 |
