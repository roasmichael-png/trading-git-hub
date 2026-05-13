import time
import pandas as pd
from scanner.client import get_client
from scanner.data import fetch_daily_bars
from scanner.indicators import add_indicators, check_signals

BATCH_SIZE = 50


def get_universe() -> list[str]:
    client = get_client()
    assets = client.list_assets(status="active", asset_class="us_equity")
    return [
        a.symbol for a in assets
        if a.tradable and a.fractionable and "." not in a.symbol
    ]


def run_scan() -> list[dict]:
    symbols = get_universe()
    print(f"Scanning {len(symbols)} symbols...")

    hits = []
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i: i + BATCH_SIZE]
        try:
            bars = fetch_daily_bars(batch)
        except Exception as e:
            print(f"  batch {i//BATCH_SIZE + 1} error: {e}")
            time.sleep(2)
            continue

        for sym, df in bars.items():
            try:
                df = add_indicators(df)
                if check_signals(df):
                    last = df.iloc[-1]
                    hits.append({
                        "symbol": sym,
                        "close": round(last["close"], 2),
                        "sma200": round(last["sma200"], 2),
                        "pct_from_200": round((last["close"] / last["sma200"] - 1) * 100, 2),
                        "srsi_k": round(last["srsi_k"], 1),
                        "srsi_d": round(last["srsi_d"], 1),
                        "macd": round(last["macd"], 2),
                        "macd_signal": round(last["macd_signal"], 2),
                    })
            except Exception:
                continue

        time.sleep(0.3)  # stay under rate limits

    return hits
