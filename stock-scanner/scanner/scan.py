import time
import pandas as pd
from scanner.client import get_client
from scanner.data import fetch_daily_bars, fetch_crypto_bars
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
    "CSX", "MCHP", "ANSS", "KDP", "EXC", "GFS", "RIVN", "LCID", "SIRI", "FITB",
    "HON", "PDD", "CDW", "CTAS", "AEP", "LULU", "EBAY", "HON", "REGN", "IDXX",
]

TOP_ETFS = [
    "SPY", "QQQ", "IVV", "VTI", "VOO", "VEA", "IEFA", "AGG", "BND", "VTV",
    "IJH", "IJR", "GLD", "VUG", "VWO", "EFA", "LQD", "HYG", "IWM", "TLT",
    "IWF", "VIG", "XLF", "IEMG", "IWD", "IAU", "ITOT", "SCHB", "VB", "VO",
    "SCHD", "SPDW", "SPEM", "VXUS", "BNDX", "XLK", "VNQ", "XLE", "XLV", "XLI",
    "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC", "ARKK", "ARKG", "ARKW", "ARKF",
]

TOP_CRYPTOS = [
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "DOGE/USD", "ADA/USD",
    "AVAX/USD", "LINK/USD", "DOT/USD", "LTC/USD", "BCH/USD", "UNI/USD",
    "AAVE/USD", "ALGO/USD", "ATOM/USD", "MATIC/USD", "SHIB/USD", "MKR/USD",
    "CRV/USD", "GRT/USD", "BAT/USD", "SUSHI/USD", "XTZ/USD", "YFI/USD",
]


def _scan_symbols(symbols: list[str], fetch_fn) -> list[dict]:
    hits = []
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i: i + BATCH_SIZE]
        try:
            bars = fetch_fn(batch)
        except Exception as e:
            print(f"  batch error: {e}")
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
        time.sleep(0.3)
    return hits


def get_universe() -> list[str]:
    return list(dict.fromkeys(QQQ_HOLDINGS))


def run_scan() -> list[dict]:
    stocks = list(dict.fromkeys(QQQ_HOLDINGS + TOP_ETFS))
    cryptos = TOP_CRYPTOS

    print(f"Scanning {len(stocks)} stocks/ETFs + {len(cryptos)} cryptos...")

    hits = _scan_symbols(stocks, fetch_daily_bars)
    hits += _scan_symbols(cryptos, fetch_crypto_bars)

    return hits
