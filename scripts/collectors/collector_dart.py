"""OpenDartReader 기반 DART 공시 수집기 — 조회 전용.

전자공시(DART) 공시 목록을 종목/기간별로 수집한다. (지침서 3장 "권장 우선순위" 2순위 소스)
공시 발표 시각과 거래량/주가 급등 시점의 시차 분석(1.4 (G))에 사용할 원시 데이터를 만든다.

이 모듈은 조회 전용이며 어떤 주문/매매 기능도 포함하지 않는다 (지침서 2장 원칙).
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import OpenDartReader

from scripts.utils.config_loader import load_config
from scripts.utils.logger import get_logger

logger = get_logger("collector_dart")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _get_client(api_key: str | None = None) -> OpenDartReader:
    if api_key is None:
        cfg = load_config()
        api_key = cfg["collectors"]["dart"]["api_key"]
    if not api_key:
        raise ValueError(
            "DART_API_KEY가 설정되지 않았습니다. .env에 DART_API_KEY를 입력하세요 "
            "(.env.example 참고)."
        )
    return OpenDartReader(api_key)


def get_disclosure_list(
    ticker: str,
    start_date: str,
    end_date: str,
    api_key: str | None = None,
) -> pd.DataFrame:
    """종목의 기간별 공시 목록 (접수일자, 보고서명, 제출인 등)."""
    dart = _get_client(api_key)
    return dart.list(ticker, start=start_date, end=end_date)


def collect_and_save(
    ticker: str,
    start_date: str,
    end_date: str,
    out_dir: str | Path | None = None,
    api_key: str | None = None,
) -> None:
    """단일 종목의 공시 목록을 수집해 data/raw/에 저장한다."""
    cfg = load_config()
    interval = cfg.get("collectors", {}).get("dart", {}).get("request_interval_sec", 0.5)

    raw_dir = Path(out_dir) if out_dir else _PROJECT_ROOT / cfg["paths"]["data_raw"]
    ticker_dir = raw_dir / "dart" / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"공시 목록 수집 시작: {ticker} ({start_date}~{end_date})")

    disclosures = get_disclosure_list(ticker, start_date, end_date, api_key=api_key)
    disclosures.to_csv(ticker_dir / "disclosures.csv", index=False, encoding="utf-8-sig")
    time.sleep(interval)

    logger.info(f"공시 목록 수집 완료: {ticker} -> {ticker_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OpenDartReader 기반 DART 공시 수집")
    parser.add_argument("ticker", help="종목코드 (예: 005930)")
    parser.add_argument("start_date", help="YYYY-MM-DD 또는 YYYYMMDD")
    parser.add_argument("end_date", help="YYYY-MM-DD 또는 YYYYMMDD")
    args = parser.parse_args()

    collect_and_save(args.ticker, args.start_date, args.end_date)
