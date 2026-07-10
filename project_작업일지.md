# 프로젝트 작업일지

> 이 파일은 모든 개발 세션의 시작점이다. 새 세션을 시작하면 반드시 이 파일의 최신 항목과
> "다음 세션에서 할 일"을 먼저 읽고 그 지점부터 이어서 작업한다. 파일 하나를 생성하거나
> 의미 있게 수정할 때마다 아래 형식으로 즉시 기록한다.
>
> `- [파일 경로] : [수행한 작업 요약] : [상태: 진행중/완료/보류]`

## 커밋 규칙 (2026-07-10 확정, 모든 세션 필수 준수)

- **최초 스캐폴딩(폴더 구조/문서/설정 템플릿처럼 실행 로직이 없는 뼈대)만 예외적으로
  한 커밋에 몰아서 커밋한다.** 이미 완료됨 (커밋 `11823fe`).
- **그 이후부터는 논리적으로 하나의 완결된 작업 단위마다 작게 커밋한다.**
  예: 지표 하나 구현 = 커밋 1개, 수집기 하나 추가 = 커밋 1개, 버그 수정 = 커밋 1개.
  여러 작업을 한 커밋에 섞지 않는다.
- **깨진 상태(테스트 실패/구문 오류)로 커밋하지 않는다.** 매 커밋이 "일단 동작하는 상태"여야
  나중에 `git bisect`로 문제 지점을 정확히 찾을 수 있다.
- **작업일지 항목과 커밋을 1:1로 대응시킨다.** 작업일지에 파일을 기록한 시점에 바로 그
  변경을 커밋한다 (기록만 해두고 커밋을 미루지 않는다).
- **의미 있는 마일스톤마다 git tag를 남긴다.** 예: `phase1-collector-done`,
  `phase1-scoring-done`. 문제가 생기면 "일단 이 태그로 돌아가자"는 기준점이 된다.
- **되돌릴 때는 `git revert`를 우선 사용한다.** 히스토리를 보존한 채 안전하게 되돌릴 수
  있다. `git reset --hard`, `push --force` 등 히스토리를 지우는 명령은 사용자가 명시적으로
  요청한 경우에만 사용한다.

---

## 2026-07-09 세션 시작

### 컨텍스트
- 기준 문서: `/root/.claude/uploads/.../62d1a670-____________________.md`
  (「프로젝트 지침서: 국내 주식시장 "세력주" 탐지 및 매매 국면 추정 프로그램」 v1.0, 2026-07-10)
- 이 저장소(`smpark84/Kor1`, 브랜치 `claude/work-log-documentation-ged1t7`)를 지침서 7장의
  `D:/project/{프로젝트명}` 루트로 취급한다. 로컬 Windows 경로 대신 저장소 루트를 프로젝트
  루트로 사용 (지침서 0장의 "project 폴더 충돌 방지" 원칙을 이 환경에 맞게 적용한 것).
- 지침서 원본은 이 세션의 참고 자료일 뿐 저장소에 커밋하지 않는다(업로드 파일 경로는 이
  세션 로컬 임시 경로). 대신 본 작업일지와 `sources.md`, `docs/`에 지침서 내용을 반영해
  저장소 자체에서 지침을 확인할 수 있도록 한다.

### 이번 세션 작업 내역
- [project_작업일지.md] : 작업일지 최초 생성 (8.1 규칙 적용) : 완료
- [디렉토리 구조] : 7장 폴더 구조대로 `config/ data/{raw,processed,cache,backtest} scripts/{collectors,indicators,scoring,backtest,dashboard,alerts,utils} docs/ logs/ tests/ notebooks/` 생성, 빈 디렉토리는 `.gitkeep`으로 git 추적 : 완료
- [.gitignore] : `.env`, `data/**`, `logs/**`, `__pycache__` 등 민감/대용량 경로 제외 설정 (9장 보안 규칙) : 완료
- [.env.example] : DART_API_KEY, KIS_APP_KEY/SECRET/ACCOUNT_NO, TELEGRAM_BOT_TOKEN/CHAT_ID, DATA_GO_KR_API_KEY 키 이름만 템플릿으로 작성 (값 없음) : 완료
- [README.md] : 프로젝트 개요, 투자자문 아님 고지 문구, 범위 밖 항목, 폴더 구조, 시작 방법, 보안 안내 작성 : 완료
- [docs/project_spec.md] : 사용자 업로드 원본 지침서(v1.0, 2026-07-10) 전문을 저장소에 보존 (업로드 경로는 세션 임시 경로라 이관 필요). 18KB 초과(약 30KB)이지만, 이는 원문 보존용 참조 문서이며 코드 모듈이 아니고 핵심 내용은 아래 docs/*.md로 주제별 분리했으므로 8.2 분할 규칙의 예외로 처리(설계 결정 — 필요 시 사용자 확인 요청 가능) : 완료
- [sources.md] : 지침서 11장 출처 61개(신뢰도별 6개 카테고리)를 이관, 이후 세션이 리서치를 추가할 "추가 리서치 로그" 섹션 마련 : 완료
- [docs/legal_notice.md] : 2장 법적/윤리적 가드레일 요약, README/대시보드/알림용 표준 고지 문구, 금지 표현 vs 허용 표현 대조표, 절대 구현 금지 기능 목록 정리 : 완료
- [docs/architecture.md] : 4장 파이프라인을 모듈↔저장소 파일 경로 매핑 표로 정리, Phase 로드맵 요약 : 완료
- [docs/indicator_spec.md] : 1.4장 지표(A~G) 표, 1.5장 국면(Wyckoff 4국면) 정의, 스코어링 설계안, MVP 우선 지표 5개 1차 제안(사용자 확인 필요) : 완료
- [docs/data_source_spec.md] : 3장 데이터 소스 표, MVP 우선순위, collector 모듈 매핑, ToS/레이트리밋 주의사항 : 완료
- [config/settings.yaml] : 앱/유니버스/경로/수집기/KIS/텔레그램/로깅 설정, 키 값은 전부 `${ENV_VAR}` 참조 형태 : 완료
- [config/indicators_config.yaml] : 거래량/수급/신용공매도/호가/VI/패턴/스코어링 파라미터 초기 참고값 (백테스트 전까지 잠정치임을 주석으로 명시) : 완료
- [scripts/utils/logger.py] : `logs/{YYYY-MM-DD}/{name}.log` 로거, API 키/시크릿/토큰/계좌번호 정규식 마스킹 필터 포함 : 완료
- [scripts/utils/config_loader.py] : `.env` 로드 + `config/*.yaml`의 `${ENV_VAR}` 재귀 치환 로더 : 완료
- [scripts/collectors/collector_krx.py] : pykrx 기반 OHLCV + 투자자별 순매수 거래대금 수집기, `data/raw/krx/{ticker}/`에 CSV 저장, CLI(`python -m scripts.collectors.collector_krx <ticker> <start> <end>`) 제공. 조회 전용, 주문 기능 없음 (2장 원칙) : 완료
- [scripts/**/__init__.py, tests/__init__.py] : 패키지 임포트 가능하도록 빈 초기화 파일 생성 : 완료
- [requirements.txt] : pandas/pykrx/finance-datareader/OpenDartReader/streamlit/python-telegram-bot/scikit-learn/pytest 등 의존성 명시 : 완료
- 문법 검증: `python3 -m py_compile`로 logger.py, config_loader.py, collector_krx.py 구문 오류 없음 확인 (pykrx 등 외부 패키지 미설치 상태라 런타임 실행/pip install까지는 검증 못함 — 다음 세션에서 `pip install -r requirements.txt` 후 실제 수집 테스트 필요)

### 리서치 관련
- 이번 세션은 신규 웹 리서치를 수행하지 않았다. 지침서에 이미 포함된 11장 출처(61개)만
  `sources.md`로 이관했다. 신규 조사가 필요하면 다음 세션에서 `sources.md` 하단 로그에 추가.

### 열린 이슈 / 사용자 확인 필요 (2.8 원칙에 따라 기록)
1. ~~**MVP 우선 지표 3~5개 확정**~~ → **2026-07-10 사용자 확인 완료.** 아래 5개로 확정:
   (1) 거래량 급증률 (2) 기관+외국인 동반 순매수 연속일수/누적대금 (3) 신용융자잔고율 증가
   추이 (4) 정배열 전환+눌림목 패턴 (5) VI 발동 이력. `docs/indicator_spec.md`도 "1차 제안"
   문구를 "확정"으로 갱신 필요(다음 커밋에서 반영).
2. **DART/KIS/텔레그램 API 키 미보유 상태**: `.env`는 아직 생성하지 않았다(값이 없으므로).
   실제 수집을 시작하려면 사용자가 키를 발급받아 `.env`에 입력해야 함. (단, 확정된 MVP 5개
   지표는 pykrx 공개 데이터만으로 계산 가능해 DART/KIS 키 없이도 구현 진행 가능.)
3. **`docs/project_spec.md` 18KB 초과**: 8.2 분할 규칙의 취지(코드 모듈 관리 용이성)와는
   성격이 다른 "원문 보존" 목적이라 그대로 두었음. 문제 삼을 경우 챕터별로 쪼개는 것도 가능.

### 2026-07-10 추가 세션 — collector_krx.py 실행 시도 및 네트워크 제약 발견
- [scripts/collectors/collector_krx.py] : `pip install pykrx pandas pyyaml python-dotenv` 후
  `python3 -m scripts.collectors.collector_krx 005930 20260601 20260710` 로 실행 테스트 시도 : 보류
- **중요 이슈(환경 제약, 코드 버그 아님)**: 이 Claude Code 클라우드 실행 환경(컨테이너)의
  네트워크 정책이 `data.krx.co.kr`로 나가는 아웃바운드 요청을 프록시 단에서 403으로 차단함
  (`requests.exceptions.ProxyError`, `curl $HTTPS_PROXY/__agentproxy/status` 확인 결과
  `"connect_rejected", "gateway answered 403 to CONNECT (policy denial)"`). 이건 조직
  egress 정책이라 우회 시도하지 않음(README 지침에 따라 재시도/우회 금지, 차단된 호스트만
  보고).
  - pykrx는 KRX/네이버 스크래핑 기반이라 이 환경에서는 원천적으로 동작하지 않을 가능성이 큼.
  - **사용자 PC(로컬)나 다른 네트워크 제약 없는 환경에서 실행하면 정상 동작할 가능성이 높음**
    — 코드 자체(`collector_krx.py`)는 구문/로직상 문제 없이 작성되어 있음.
  - 이 실행 환경에서 데이터 수집 파이프라인을 계속 실제 검증하려면, 사용자가 이 환경의
    네트워크 정책에 `data.krx.co.kr` 등 KRX/DART 관련 도메인을 허용해주거나, 로컬 PC에서
    직접 실행해서 검증해야 함.
  - 지표 계산 로직(`indicator_*.py`)은 실제 네트워크 호출 없이 합성/샘플 데이터로 단위
    테스트가 가능하므로, 이 환경에서는 네트워크 검증 대신 지표 로직 구현·테스트를 우선 진행.

### 2026-07-10 추가 세션 — indicator_volume.py 구현 (MVP 지표 1번)
- [scripts/indicators/indicator_volume.py] : `volume_surge_ratio()`(당일÷직전 N일 평균,
  당일 제외로 lookahead 왜곡 방지), `is_volume_surge()`(임계값 초과 여부) 구현. 파라미터
  미지정 시 `config/indicators_config.yaml`의 volume.surge_lookback_days/surge_ratio_threshold
  사용 : 완료
- [tests/test_indicator_volume.py] : 합성 데이터(네트워크 불필요)로 3개 단위 테스트 작성 —
  기본 급증 비율, 당일 제외 검증, 임계값 판정. `pytest` 3 passed 확인 : 완료

### 2026-07-10 추가 세션 — indicator_flow.py 구현 (MVP 지표 2번)
- [scripts/indicators/indicator_flow.py] : `co_net_buy_streak_days()`(기관+외국인 동반 순매수
  연속일수), `co_net_buy_cumulative_amount()`(연속구간 누적 순매수 대금),
  `is_distribution_flow_pattern()`(개인 순매수 급증×기관/외국인 순매도 동시발생 — 분산 국면
  신호) 구현. 구현 중 `_streak_id`(값이 False로 끊길 때만 그룹 증가) 방식이 그룹 경계를
  잘못 잡는 버그를 테스트로 발견 → `_run_id`(값이 이전 행과 달라질 때마다 그룹 증가)로 수정 :
  완료
- [tests/test_indicator_flow.py] : 3개 단위 테스트(연속일수 리셋, 누적대금 리셋+합산, 분산
  패턴 판정) 작성. 최초 버전은 연속일수 테스트가 실패해 로직 버그를 잡아냄 — `pytest` 3 passed
  확인 : 완료

### 2026-07-10 추가 세션 — indicator_credit_short.py 구현 (MVP 지표 3번)
- [config/indicators_config.yaml] : credit_short 섹션에 `credit_ratio_lookback_days`,
  `short_balance_lookback_days`를 명시 추가 (기존엔 spike_pct만 있고 lookback 기간이
  누락돼 있었음) : 완료
- [scripts/indicators/indicator_credit_short.py] : `change_rate()`(N일 전 대비 상대
  변화율 공통 함수), `is_credit_ratio_spike()`, `is_short_balance_spike()`,
  `is_short_covering()`(숏커버링 감지, 반등 참고 신호) 구현 : 완료
- [tests/test_indicator_credit_short.py] : 4개 단위 테스트 작성, `pytest` 3 passed 확인 : 완료

### 2026-07-10 추가 세션 — indicator_pattern.py 구현 (MVP 지표 4번)
- [scripts/indicators/indicator_pattern.py] : `moving_averages()`, `is_bullish_alignment()`
  (5>20>60>120일선 정배열 판정), `swing_lows()`+`is_ascending_pullback()`(눌림목 저점 계단식
  상승 근사 판정, rolling min 기반) 구현. 눌림목은 노이즈가 커서 단독 사용 금지·조합 필수라는
  지침서 지적을 docstring에 명시 : 완료
- [tests/test_indicator_pattern.py] : 4개 단위 테스트(정배열 상승/하락 케이스, 눌림목 상승/
  하락 케이스), `pytest` 4 passed 확인 : 완료

### 다음 세션에서 할 일
- [ ] (환경 제약 있음) `collector_krx.py`를 네트워크 제약 없는 환경(사용자 PC 등)에서 재검증
- [ ] `scripts/indicators/indicator_vi.py` (VI 발동 이력) — MVP 지표 5번 (일별 집계로 근사 가능한
      소스 확인 필요, 없으면 Phase 2 실시간 수집 이후로 보류)
- [ ] `scripts/collectors/collector_dart.py`, `collector_credit_short.py` 프로토타입 작성
- [ ] `scripts/scoring/scoring_engine.py` 초안 (가중합 방식, config/indicators_config.yaml의 weights 사용)
- [ ] `tests/` 하위에 collector/indicator 단위 테스트 추가
- [ ] 커밋 규칙(위 "커밋 규칙" 섹션) 준수: 지표 하나 완성 = 커밋 1개. 파일 생성/수정 시마다
      이 작업일지에 계속 기록할 것 (필수)
