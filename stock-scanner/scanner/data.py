import pandas as pd
from datetime import datetime, timedelta
from alpaca_trade_api.rest import TimeFrame
from scanner.client import get_client


def fetch_daily_bars(symbols: list[str], days: int = 300) -> dict[str, pd.DataFrame]:
    client = get_client()
    end = datetime.now()
    start = end - timedelta(days=days)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    results = {}
    for sym in symbols:
        try:
            raw = client.get_bars(
                sym,
                TimeFrame.Day,
                start_str,
                end_str,
                adjustment="raw",
                feed="iex",
            ).df
            if raw.empty or len(raw) < 30:
                continue
            raw.index = pd.to_datetime(raw.index)
            results[sym] = raw
        except Exception:
            continue

    return results
