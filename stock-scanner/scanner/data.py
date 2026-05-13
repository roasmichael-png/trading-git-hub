import pandas as pd
from datetime import datetime, timedelta
from alpaca_trade_api.rest import TimeFrame
from scanner.client import get_client


def fetch_daily_bars(symbols: list[str], days: int = 300) -> dict[str, pd.DataFrame]:
    client = get_client()
    end = datetime.now()
    start = end - timedelta(days=days)

    raw = client.get_bars(
        symbols,
        TimeFrame.Day,
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        adjustment="raw",
        feed="iex",
    ).df

    if raw.empty:
        return {}

    results = {}
    if isinstance(raw.index, pd.MultiIndex):
        for sym in raw.index.get_level_values("symbol").unique():
            df = raw.xs(sym, level="symbol").copy()
            df.index = pd.to_datetime(df.index)
            results[sym] = df
    else:
        raw.index = pd.to_datetime(raw.index)
        results[symbols[0]] = raw

    return results
