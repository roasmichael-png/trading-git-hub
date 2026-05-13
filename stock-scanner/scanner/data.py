import pandas as pd
from datetime import datetime, timedelta
from alpaca_trade_api.rest import TimeFrame
from scanner.client import get_client


def _date_range(days: int):
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_daily_bars(symbols: list[str], days: int = 300) -> dict[str, pd.DataFrame]:
    client = get_client()
    start_str, end_str = _date_range(days)
    results = {}
    for sym in symbols:
        try:
            raw = client.get_bars(
                sym, TimeFrame.Day, start_str, end_str,
                adjustment="raw", feed="iex",
            ).df
            if raw.empty or len(raw) < 30:
                continue
            raw.index = pd.to_datetime(raw.index)
            results[sym] = raw
        except Exception:
            continue
    return results


def fetch_crypto_bars(symbols: list[str], days: int = 300) -> dict[str, pd.DataFrame]:
    client = get_client()
    start_str, end_str = _date_range(days)
    results = {}
    for sym in symbols:
        try:
            raw = client.get_crypto_bars(sym, TimeFrame.Day, start_str, end_str).df
            if raw.empty or len(raw) < 30:
                continue
            if isinstance(raw.index, pd.MultiIndex):
                raw = raw.xs(sym, level="symbol")
            raw.index = pd.to_datetime(raw.index)
            results[sym] = raw
        except Exception:
            continue
    return results

