"""pykrx 기반 KRX 데이터 수집기 — OHLCV 및 투자자별 매매동향.

Phase 1(MVP) 배치 수집 모듈. 일별 시세와 기관/외국인/개인 순매수 데이터를 수집해
data/raw/에 종목별 CSV로 저장한다. (지침서 3장 "권장 우선순위" 1순위 소스)

이 모듈은 조회 전용이며 어떤 주문/매매 기능도 포함하지 않는다 (지침서 2장 원칙).
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from pykrx import stock

from scripts.utils.config_loader import load_config
from scripts.utils.logger import get_logger

logger = get_logger("collector_krx")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_ohlcv(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """일별 OHLCV. 날짜는 'YYYYMMDD' 형식."""
    df = stock.get_market_ohlcv(start_date, end_date, ticker)
    df.index.name = "date"
    return df


def get_investor_trading_value(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """투자자별(기관/외국인/개인 등) 순매수 거래대금."""
    df = stock.get_market_trading_value_by_date(start_date, end_date, ticker)
    df.index.name = "date"
    return df


def get_market_tickers(date_str: str, market: str = "ALL") -> list[str]:
    """특정 일자 기준 상장 종목코드 목록. market: KOSPI | KOSDAQ | ALL"""
    if market == "ALL":
        return stock.get_market_ticker_list(date_str, market="KOSPI") + \
            stock.get_market_ticker_list(date_str, market="KOSDAQ")
    return stock.get_market_ticker_list(date_str, market=market)


def collect_and_save(ticker: str, start_date: str, end_date: str, out_dir: str | Path | None = None) -> None:
    """단일 종목의 OHLCV + 투자자별 매매동향을 수집해 data/raw/에 저장한다."""
    cfg = load_config()
    interval = cfg.get("collectors", {}).get("krx", {}).get("request_interval_sec", 1.0)

    raw_dir = Path(out_dir) if out_dir else _PROJECT_ROOT / cfg["paths"]["data_raw"]
    ticker_dir = raw_dir / "krx" / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"수집 시작: {ticker} ({start_date}~{end_date})")

    ohlcv = get_ohlcv(ticker, start_date, end_date)
    ohlcv.to_csv(ticker_dir / "ohlcv.csv", encoding="utf-8-sig")
    time.sleep(interval)

    flow = get_investor_trading_value(ticker, start_date, end_date)
    flow.to_csv(ticker_dir / "investor_flow.csv", encoding="utf-8-sig")
    time.sleep(interval)

    logger.info(f"수집 완료: {ticker} -> {ticker_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="pykrx 기반 KRX 데이터 수집")
    parser.add_argument("ticker", help="종목코드 (예: 005930)")
    parser.add_argument("start_date", help="YYYYMMDD")
    parser.add_argument("end_date", help="YYYYMMDD")
    args = parser.parse_args()

    collect_and_save(args.ticker, args.start_date, args.end_date)
