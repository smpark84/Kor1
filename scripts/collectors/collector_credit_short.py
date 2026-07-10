"""신용잔고·공매도 잔고 데이터 수집기 — 조회 전용.

공매도 잔고는 pykrx(stock.get_shorting_balance_by_date)로 조회 가능해 구현했다.

신용융자잔고는 pykrx에 해당 API가 없고 금융투자협회 FreeSIS(3장 데이터 소스 표,
https://freesis.kofia.or.kr)에서 웹 스크래핑으로 가져와야 한다. 이 실행 환경은
네트워크 정책상 외부 사이트 접근이 막혀 있어(작업일지 참고) 실제 페이지 구조를
확인·검증하며 스크래퍼를 작성할 수 없다. 검증되지 않은 스크래핑 코드를 추측으로
작성하면 실제 사이트 구조와 어긋나 조용히 실패하거나 잘못된 데이터를 수집할
위험이 있어, 신용잔고 수집 함수는 의도적으로 미구현(NotImplementedError) 상태로
남기고 다음 세션(네트워크 제약 없는 환경)에서 FreeSIS 페이지를 직접 확인하며
구현하도록 안내한다.
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from pykrx import stock

from scripts.utils.config_loader import load_config
from scripts.utils.logger import get_logger

logger = get_logger("collector_credit_short")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_short_balance(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """일자별 공매도 잔고 현황 (공매도잔고, 상장주식수, 공매도금액, 시가총액, 비중)."""
    df = stock.get_shorting_balance_by_date(start_date, end_date, ticker)
    df.index.name = "date"
    return df


def get_credit_balance(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """일자별 신용거래융자잔고. 미구현 — 모듈 상단 docstring 참고."""
    raise NotImplementedError(
        "신용융자잔고 수집은 미구현 상태입니다. pykrx는 해당 데이터를 제공하지 않고 "
        "금융투자협회 FreeSIS 스크래핑이 필요합니다. 네트워크 제약이 없는 환경에서 "
        "실제 페이지 구조를 확인하며 구현해야 합니다 "
        "(docs/data_source_spec.md, project_작업일지.md 참고)."
    )


def collect_and_save(ticker: str, start_date: str, end_date: str, out_dir: str | Path | None = None) -> None:
    """단일 종목의 공매도 잔고를 수집해 data/raw/에 저장한다. (신용잔고는 미구현)"""
    cfg = load_config()
    interval = cfg.get("collectors", {}).get("krx", {}).get("request_interval_sec", 1.0)

    raw_dir = Path(out_dir) if out_dir else _PROJECT_ROOT / cfg["paths"]["data_raw"]
    ticker_dir = raw_dir / "credit_short" / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"공매도 잔고 수집 시작: {ticker} ({start_date}~{end_date})")

    short_balance = get_short_balance(ticker, start_date, end_date)
    short_balance.to_csv(ticker_dir / "short_balance.csv", encoding="utf-8-sig")
    time.sleep(interval)

    logger.info(f"공매도 잔고 수집 완료: {ticker} -> {ticker_dir} (신용잔고는 미구현)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="공매도 잔고 수집 (신용잔고는 미구현)")
    parser.add_argument("ticker", help="종목코드 (예: 005930)")
    parser.add_argument("start_date", help="YYYYMMDD")
    parser.add_argument("end_date", help="YYYYMMDD")
    args = parser.parse_args()

    collect_and_save(args.ticker, args.start_date, args.end_date)
