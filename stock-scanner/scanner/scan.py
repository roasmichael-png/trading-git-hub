import time
from scanner.data import fetch_daily_bars, fetch_crypto_bars
from scanner.indicators import add_indicators, check_signals

BATCH_SIZE = 50

# QQQ holdings
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
    "HON", "PDD", "CDW", "CTAS", "AEP", "LULU", "EBAY",
]

# SMH (VanEck Semiconductor ETF) holdings
SMH_HOLDINGS = [
    "NVDA", "TSM", "AVGO", "ASML", "AMD", "QCOM", "MU", "AMAT", "TXN", "LRCX",
    "KLAC", "ADI", "MRVL", "ON", "NXPI", "MCHP", "TER", "ENTG", "STM", "WOLF",
]

# VGT (Vanguard IT ETF) top holdings
VGT_HOLDINGS = [
    "AAPL", "NVDA", "MSFT", "AVGO", "AMD", "ORCL", "CRM", "ADBE", "ACN", "IBM",
    "TXN", "QCOM", "AMAT", "MU", "CSCO", "KLAC", "LRCX", "NOW", "PANW", "INTC",
]

# BOTZ (Global X Robotics & AI) holdings
BOTZ_HOLDINGS = [
    "ISRG", "KEYS", "AZENTA", "ONTO", "TRMB", "CGNX", "TER", "ZBRA", "ABB", "FANUY",
]

# URA (Global X Uranium ETF) holdings
URA_HOLDINGS = [
    "CCJ", "NXE", "DNN", "UEC", "UUUU", "NNE", "SMR", "LEU", "BWXT",
]

# QTUM (Defiance Quantum ETF) holdings
QTUM_HOLDINGS = [
    "IONQ", "QBTS", "RGTI", "IBM", "GOOGL", "MSFT", "NVDA", "HON", "AMZN",
]

# SCHG (Schwab Large-Cap Growth) top holdings
SCHG_HOLDINGS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "LLY",
    "JPM", "V", "XOM", "COST", "UNH", "MA", "ORCL", "WMT", "CRM", "NFLX",
]

# Elite long-term + blast-off individual stocks
ELITE_STOCKS = [
    # Elite Long-Term
    "NVDA", "MSFT", "AMZN", "META", "GOOGL", "AVGO", "TSM", "PLTR", "TSLA", "AMD",
    # Aggressive Blast Off
    "RKLB", "IONQ", "SOUN", "TEM", "SMR", "AI", "SERV", "ASTS", "NTR",
    # Sector winners
    "COIN", "MSTR", "MARA", "RIOT",   # crypto infrastructure
    "LMT", "RTX", "NOC", "GD",        # defense
    "EQIX", "DLR",                     # data centers
    "SNOW", "CRM", "NOW",              # cloud
    "RXRX", "SDGR",                    # AI healthcare
    "QBTS", "RGTI",                    # quantum
    "UBER", "LYFT",                    # autonomous vehicles
    "RKLB", "SPCE",                    # space
    "VST", "NNE",                      # nuclear
]

# Top ETFs
TOP_ETFS = [
    "QQQ", "VOO", "VTI", "SPY", "IVV", "VUG", "SCHG", "VGT", "SMH", "SOXX",
    "BOTZ", "URA", "QTUM", "IWM", "IWF", "GLD", "IAU", "TLT", "HYG", "LQD",
    "XLK", "XLE", "XLF", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLC",
    "ARKK", "ARKG", "ARKW", "ARKF", "SCHD", "VNQ", "VEA", "VWO", "EFA", "EEM",
    "IEFA", "IEMG", "AGG", "BND", "VCIT", "VIG", "USMV", "SPDW", "SPEM",
]

# Crypto
CRYPTOS = [
    # Core
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "LINK/USD",
    # Aggressive
    "AVAX/USD", "RNDR/USD", "SUI/USD", "NEAR/USD", "FET/USD",
    # Others Alpaca supports
    "DOGE/USD", "ADA/USD", "DOT/USD", "LTC/USD", "BCH/USD",
    "UNI/USD", "AAVE/USD", "ALGO/USD", "ATOM/USD", "MATIC/USD",
    "MKR/USD", "CRV/USD", "GRT/USD", "BAT/USD",
]


def _all_stocks() -> list[str]:
    combined = (
        QQQ_HOLDINGS + SMH_HOLDINGS + VGT_HOLDINGS + BOTZ_HOLDINGS +
        URA_HOLDINGS + QTUM_HOLDINGS + SCHG_HOLDINGS + ELITE_STOCKS
    )
    return list(dict.fromkeys(combined))  # dedupe, preserve order


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
                        "close":       round(last["close"], 2),
                        "srsi_k":      round(last["srsi_k"], 1),
                        "srsi_d":      round(last["srsi_d"], 1),
                        "macd":        round(last["macd"], 2),
                        "macd_signal": round(last["macd_signal"], 2),
                    })
            except Exception:
                continue
        time.sleep(0.3)
    return hits


def run_scan() -> list[dict]:
    stocks = _all_stocks()
    etfs   = list(dict.fromkeys(TOP_ETFS))
    all_stocks_etfs = list(dict.fromkeys(stocks + etfs))

    print(f"Scanning {len(all_stocks_etfs)} stocks/ETFs + {len(CRYPTOS)} cryptos...")
    hits  = _scan_symbols(all_stocks_etfs, fetch_daily_bars)
    hits += _scan_symbols(CRYPTOS, fetch_crypto_bars)
    return hits
