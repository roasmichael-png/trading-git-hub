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
    "SMCI", "ACMR", "CRDO", "FORM", "MKSI", "ONTO", "PI", "MPWR", "SWKS", "QRVO",
]

# VGT (Vanguard IT ETF) top holdings
VGT_HOLDINGS = [
    "AAPL", "NVDA", "MSFT", "AVGO", "AMD", "ORCL", "CRM", "ADBE", "ACN", "IBM",
    "TXN", "QCOM", "AMAT", "MU", "CSCO", "KLAC", "LRCX", "NOW", "PANW", "INTC",
    "NET", "GTLB", "MDB", "ESTC", "CFLT", "DDOG", "ZS", "SNOW",
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

# S&P 500 Financials
SP500_FINANCIALS = [
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "BX", "KKR", "APO",
    "AXP", "COF", "DFS", "SYF", "SPGI", "MCO", "ICE", "CME", "CBOE", "SCHW",
    "USB", "PNC", "TFC", "MTB", "RF", "CFG", "HBAN", "KEY", "FITB", "ZION",
    "MET", "PRU", "AFL", "ALL", "TRV", "CB", "AIG", "HIG", "PGR", "L",
    "HOOD", "SOFI", "AFRM", "UPST", "LC", "OPEN",
]

# S&P 500 Healthcare
SP500_HEALTHCARE = [
    "UNH", "JNJ", "LLY", "ABT", "TMO", "DHR", "SYK", "BSX", "EW", "MDT",
    "ISRG", "IQV", "A", "HOLX", "PODD", "TMDX", "DXCM", "IDXX", "ALGN", "REGN",
    "VRTX", "BIIB", "GILD", "AMGN", "BMY", "MRK", "PFE", "ABBV", "ZTS", "CVS",
    "CI", "HUM", "ELV", "CNC", "MOH", "GEHC", "BAX", "BDX", "CAH", "MCK",
    "MRNA", "BNTX", "NVAX", "RXRX", "SDGR", "EXAS", "GH", "ILMN", "PACB", "BEAM",
    "HIMS", "DOCS", "ACCD", "ONEM", "PHR", "OMCL", "NVCR", "IONS", "ALNY", "SRPT",
]

# S&P 500 Energy
SP500_ENERGY = [
    "XOM", "CVX", "COP", "EOG", "SLB", "HAL", "MPC", "PSX", "VLO", "DVN",
    "OXY", "HES", "BKR", "FANG", "MRO", "APA", "CTRA", "PR", "SM", "MGY",
    "ENPH", "FSLR", "ARRY", "RUN", "NOVA", "SEDG", "MAXN", "BE", "PLUG", "BLDP",
    "VST", "NNE", "CEG", "CCJ", "SMR", "OKLO",
]

# S&P 500 Industrials
SP500_INDUSTRIALS = [
    "CAT", "DE", "RTX", "LMT", "BA", "GE", "HON", "UPS", "FDX", "EMR",
    "ETN", "PH", "ROK", "AME", "GNRC", "IR", "TT", "CARR", "OTIS", "GD",
    "NOC", "LHX", "HII", "LDOS", "SAIC", "BAH", "CACI", "MANT",
    "AXON", "TASER", "MSI", "ARLO", "SWIR",
    "RKLB", "SPCE", "ASTS", "RDW", "LUNR",
    "DAL", "UAL", "LUV", "AAL", "JBLU", "ALK",
    "BLDR", "PHM", "DHI", "LEN", "NVR", "TOL", "KBH",
]

# S&P 500 Consumer
SP500_CONSUMER = [
    "AMZN", "HD", "LOW", "TGT", "WMT", "MCD", "SBUX", "NKE", "LULU", "CMG",
    "YUM", "QSR", "WING", "DNUT", "SHAK", "TXRH", "DINE",
    "TSLA", "F", "GM", "RIVN", "LCID", "NIO", "LI", "XPEV",
    "CHWY", "ETSY", "EBAY", "W", "OSTK",
    "SHOP", "MELI", "SE", "GRAB",
    "DKNG", "PENN", "CZR", "MGM", "WYNN", "LVS",
    "SPOT", "RBLX", "U", "EA", "TTWO",
    "ELF", "ULTA", "COTY", "EL", "LULU",
]

# High-growth / momentum individual stocks
MOMENTUM_STOCKS = [
    # AI / Software
    "PLTR", "AI", "BBAI", "SOUN", "AAON", "APP", "CELH",
    "NET", "DDOG", "SNOW", "MDB", "GTLB", "ESTC", "CFLT",
    "DUOL", "BILL", "TOST", "GLBE", "FOUR",
    # Fintech
    "PYPL", "SQ", "AFRM", "UPST", "HOOD", "SOFI", "NU",
    # Crypto infrastructure
    "COIN", "MSTR", "MARA", "RIOT", "CLSK", "BTBT", "HUT",
    # Biotech high-momentum
    "TEM", "HIMS", "ACMR", "RXRX", "BEAM", "NTLA", "CRSP",
    "IONS", "ALNY", "SRPT", "RARE", "FOLD",
    # Space / defense tech
    "RKLB", "ASTS", "LUNR", "RDW", "SPCE", "KTOS", "CACI",
    # Quantum
    "IONQ", "QBTS", "RGTI", "QUBT",
    # Nuclear / energy
    "SMR", "NNE", "OKLO", "BWXT", "LEU",
    # Semiconductors
    "SMCI", "ACMR", "CRDO", "ASML", "AEHR", "WOLF",
    # Others
    "SERV", "UBER", "LYFT", "NTR", "AXON", "VST",
]

# Elite long-term + blast-off individual stocks
ELITE_STOCKS = [
    "NVDA", "MSFT", "AMZN", "META", "GOOGL", "AVGO", "TSM", "PLTR", "TSLA", "AMD",
    "RKLB", "IONQ", "SOUN", "TEM", "SMR", "AI", "SERV", "ASTS", "NTR",
    "COIN", "MSTR", "MARA", "RIOT",
    "LMT", "RTX", "NOC", "GD",
    "EQIX", "DLR",
    "SNOW", "CRM", "NOW",
    "RXRX", "SDGR",
    "QBTS", "RGTI",
    "UBER", "LYFT",
    "SPCE", "VST", "NNE",
]

# Top ETFs
TOP_ETFS = [
    "QQQ", "VOO", "VTI", "SPY", "IVV", "VUG", "SCHG", "VGT", "SMH", "SOXX",
    "BOTZ", "URA", "QTUM", "IWM", "IWF", "GLD", "IAU", "TLT", "HYG", "LQD",
    "XLK", "XLE", "XLF", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLC",
    "ARKK", "ARKG", "ARKW", "ARKF", "SCHD", "VNQ", "VEA", "VWO", "EFA", "EEM",
    "IEFA", "IEMG", "AGG", "BND", "VCIT", "VIG", "USMV", "SPDW", "SPEM",
    "CIBR", "HACK", "BUG", "WCLD", "CLOU", "IPAY", "FINX",
    "JETS", "ROBO", "DRIV", "KARS", "BETZ",
    "IBB", "XBI", "ARKG", "PBE", "BBH",
    "REMX", "LIT", "COPX", "SIL", "GDX", "GDXJ",
    "TAN", "ICLN", "QCLN", "FAN",
]

# Crypto
CRYPTOS = [
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "LINK/USD",
    "AVAX/USD", "RNDR/USD", "SUI/USD", "NEAR/USD", "FET/USD",
    "DOGE/USD", "ADA/USD", "DOT/USD", "LTC/USD", "BCH/USD",
    "UNI/USD", "AAVE/USD", "ALGO/USD", "ATOM/USD", "MATIC/USD",
    "MKR/USD", "CRV/USD", "GRT/USD", "BAT/USD",
]


def _all_stocks() -> list[str]:
    combined = (
        QQQ_HOLDINGS + SMH_HOLDINGS + VGT_HOLDINGS + BOTZ_HOLDINGS +
        URA_HOLDINGS + QTUM_HOLDINGS + SCHG_HOLDINGS + ELITE_STOCKS +
        SP500_FINANCIALS + SP500_HEALTHCARE + SP500_ENERGY +
        SP500_INDUSTRIALS + SP500_CONSUMER + MOMENTUM_STOCKS
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
