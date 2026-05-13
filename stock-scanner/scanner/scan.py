import time
import pandas as pd
from scanner.client import get_client
from scanner.data import fetch_daily_bars
from scanner.indicators import add_indicators, check_signals

BATCH_SIZE = 50

QQQ_HOLDINGS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
    "NFLX", "TMUS", "AMD", "PEP", "CSCO", "ADBE", "INTU", "CMCSA", "TXN", "AMGN",
    "QCOM", "ISRG", "AMAT", "BKNG", "MU", "LRCX", "REGN", "KLAC", "MELI", "MDLZ",
    "PANW", "SNPS", "CDNS", "CRWD", "FTNT", "ADI", "MRVL", "ABNB", "ORLY", "CHTR",
    "WDAY", "NXPI", "MNST", "PYPL", "DXCM", "BIIB", "IDXX", "VRTX", "ADP", "GILD",
    "PAYX", "TEAM", "ODFL", "GEHC", "VRSK", "FANG", "ON", "CSGP", "ZS", "SBUX",
    "DLTR", "ROST", "FAST", "BKR", "XEL", "CTSH", "PCAR", "WBD", "ALGN", "ILMN",
    "ZM", "DDOG", "TTD", "ENPH", "MRNA", "CEG", "CPRT", "CCEP", "TTWO", "ROP",
    "CSX", "MCHP", "ANSS", "GEHC", "KDP", "EXC", "SPLK", "GFS", "RIVN", "LCID",
    "SIRI", "FITB", "HON", "PDD", "CDW", "CTAS", "VRSK", "AEP", "LULU", "EBAY",
]


def get_universe() -> list[str]:
    return list(dict.fromkeys(QQQ_HOLDINGS))  # dedupe, preserve order


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
                        "srsi_k": round(last["srsi_k"], 1),
                        "srsi_d": round(last["srsi_d"], 1),
                        "macd": round(last["macd"], 2),
                        "macd_signal": round(last["macd_signal"], 2),
                    })
            except Exception:
                continue

        time.sleep(0.3)  # stay under rate limits

    return hits
