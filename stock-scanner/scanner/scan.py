import time
from scanner.data import fetch_daily_bars
from scanner.indicators import add_indicators, check_signals

BATCH_SIZE = 50

# ─── SECTORS ──────────────────────────────────────────────────────────────────

SECTORS = {
    "🤖 AI": [
        "NVDA", "PLTR", "AI", "SOUN", "BBAI", "APP", "PATH", "SYM",
        "SNOW", "DDOG", "MDB", "GTLB", "CFLT", "NET",
        "NOW", "CRM", "WDAY", "TEAM", "DUOL", "BILL", "TOST",
        "IONQ", "QBTS", "RGTI", "QUBT",  # quantum compute
        "TSM", "ARM", "SMCI", "ACMR",
    ],

    "💻 Tech": [
        "AAPL", "MSFT", "GOOGL", "GOOG", "META", "AMZN", "TSLA",
        "AVGO", "AMD", "QCOM", "INTC", "TXN", "AMAT", "MU", "LRCX",
        "KLAC", "ADI", "MRVL", "ASML", "NXPI", "MCHP", "CRDO",
        "ADBE", "INTU", "ORCL", "IBM", "ACN", "SAP",
        "PANW", "CRWD", "ZS", "FTNT", "OKTA", "CYBR", "S", "TENB",
        "SHOP", "MELI", "SE", "GLBE", "FOUR",
        "PYPL", "SQ", "AFRM", "UPST", "SOFI", "NU", "HOOD",
    ],

    "🛡️ Defense": [
        "LMT", "RTX", "NOC", "GD", "LHX", "HII", "LDOS", "SAIC",
        "BAH", "CACI", "KTOS", "AVAV", "AXON", "BA", "GE",
        "MSI", "MANT", "MOOG", "TDG", "HEI", "TGI",
    ],

    "⚡ Energy": [
        # Oil & Gas
        "XOM", "CVX", "COP", "EOG", "SLB", "HAL", "OXY", "DVN",
        "HES", "BKR", "FANG", "MRO", "APA", "CTRA",
        # Nuclear
        "CCJ", "NXE", "DNN", "UEC", "UUUU", "SMR", "NNE", "OKLO",
        "BWXT", "LEU", "VST", "CEG",
        # Solar / Clean
        "ENPH", "FSLR", "ARRY", "RUN", "SEDG", "BE", "PLUG",
        # Power / Grid
        "PWR", "POWL", "ETN", "CARR", "MLI", "MOD", "IESC", "GE",
        "EMR", "AME", "ROK", "IR", "PH",
    ],

    "🪙 Crypto": [
        # Crypto-native stocks
        "COIN", "MSTR", "MARA", "RIOT", "CLSK", "CORZ", "CIFR",
        "BTBT", "HUT", "BITF", "WULF",
    ],

    "🚀 Space": [
        "RKLB", "ASTS", "LUNR", "PL", "IRDM", "GSAT", "RDW", "SPCE",
    ],

    "🧬 Healthcare": [
        "UNH", "JNJ", "LLY", "ABT", "TMO", "DHR", "SYK", "BSX",
        "ISRG", "DXCM", "IDXX", "ALGN", "REGN", "VRTX", "BIIB",
        "GILD", "AMGN", "MRK", "ABBV",
        "MRNA", "RXRX", "BEAM", "NTLA", "CRSP", "IONS", "ALNY",
        "SRPT", "HIMS", "TEM", "ACCD",
    ],

    "💰 Financials": [
        "JPM", "BAC", "GS", "MS", "BLK", "BX", "KKR", "APO",
        "V", "MA", "AXP", "SPGI", "MCO", "ICE", "CME",
        "SCHW", "C", "WFC",
    ],

    "🏗️ Power & Grid": [
        # Your core power/grid plays
        "FIX", "IESC", "PWR", "POWL", "ETN", "MOD", "CARR",
        "MLI", "BDC", "BE",
        # Additional industrial/grid
        "EMR", "AME", "ROK", "IR", "PH", "GNRC", "TRMB",
    ],

    "🥇 Metals & Commodities": [
        # Gold miners & ETFs
        "NEM", "AEM", "GOLD", "KGC", "AGI", "WPM", "RGLD",
        # Silver
        "AG", "PAAS", "MAG", "CDE",
        # Copper
        "FCX", "SCCO", "TECK", "HBM",
        # Broad metals ETFs
        "GLD", "IAU", "SLV", "COPX", "GDX", "GDXJ", "SIL",
        "REMX", "LIT",
    ],
}

# Top ETFs to scan alongside individual stocks
TOP_ETFS = [
    "QQQ", "VOO", "SPY", "VGT", "SMH", "SOXX",
    "BOTZ", "URA", "QTUM", "IWM", "GLD",
    "XLK", "XLE", "XLF", "XLV", "XLI", "XLY",
    "ARKK", "ARKW", "ARKQ",
    "CIBR", "HACK", "AIQ", "CHAT",
    "JETS", "ROBO", "ITA", "XAR", "ARKX",
    "TAN", "ICLN", "GRID",
    "IBB", "XBI",
    "SHLD",
]

# Build reverse lookup: symbol → sector name
_SYMBOL_TO_SECTOR: dict[str, str] = {}
for _sector, _syms in SECTORS.items():
    for _sym in _syms:
        _SYMBOL_TO_SECTOR.setdefault(_sym, _sector)


def get_sector(symbol: str) -> str:
    return _SYMBOL_TO_SECTOR.get(symbol, "📊 Other")


def _all_stocks() -> list[str]:
    combined = []
    for syms in SECTORS.values():
        combined.extend(syms)
    return list(dict.fromkeys(combined))


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
                        "symbol":      sym,
                        "sector":      get_sector(sym),
                        "close":       round(last["close"], 2),
                        "srsi_k":      round(last["srsi_k"], 1),
                        "srsi_d":      round(last["srsi_d"], 1),
                        "macd":        round(last["macd"], 2),
                        "macd_signal": round(last["macd_signal"], 2),
                        "rvol":        round(last["rvol"], 2) if "rvol" in last and last["rvol"] == last["rvol"] else 0.0,
                    })
            except Exception:
                continue
        time.sleep(0.3)
    return hits


def run_scan() -> list[dict]:
    stocks = _all_stocks()
    etfs = list(dict.fromkeys(TOP_ETFS))
    all_symbols = list(dict.fromkeys(stocks + etfs))
    print(f"Scanning {len(all_symbols)} stocks/ETFs across {len(SECTORS)} sectors...")
    return _scan_symbols(all_symbols, fetch_daily_bars)
