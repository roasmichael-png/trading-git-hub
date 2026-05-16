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

# Power / Grid / Industrial Tech
POWER_INFRA = [
    "PWR", "POWL", "ETN", "CARR", "MLI", "MOD", "IESC", "BDC",
    "OUST", "AOSL", "CLF", "RCAT", "DYN", "MISL", "BE",
    "TRMB", "IR", "AME", "ROK", "EMR", "GE", "PH",
]

# Cybersecurity
CYBERSECURITY = [
    "CRWD", "PANW", "ZS", "FTNT", "NET", "S", "CYBR", "OKTA", "RPD",
    "TENB", "VRNS", "QLYS", "SAIL", "HACK", "CIBR",
]

# Robotics / Automation
ROBOTICS = [
    "ISRG", "PATH", "SYM", "CGNX", "ZBRA", "TER", "ROK", "ABB",
    "NVDA", "TSLA", "SERV",
]

# Defense / Aerospace
DEFENSE = [
    "LMT", "RTX", "NOC", "GD", "LHX", "HII", "LDOS", "SAIC", "BAH", "CACI",
    "KTOS", "AVAV", "AXON", "BA", "GE",
]

# Space
SPACE = [
    "RKLB", "ASTS", "LUNR", "PL", "SPCE", "IRDM", "GSAT", "RDW",
]

# Crypto-infrastructure stocks
CRYPTO_INFRA_STOCKS = [
    "COIN", "MSTR", "MARA", "RIOT", "CLSK", "CORZ", "CIFR", "BTBT", "HUT",
    "HOOD", "SOFI",
]

# AI / Cloud software
AI_SOFTWARE = [
    "PLTR", "AI", "SOUN", "BBAI", "APP", "PATH", "SYM",
    "SNOW", "DDOG", "MDB", "GTLB", "ESTC", "CFLT", "NET",
    "CRWD", "NOW", "CRM", "WDAY", "TEAM", "ZM", "BILL", "TOST",
    "DUOL", "GLBE", "FOUR", "SHOP",
]

# Arm Holdings + chip design
CHIP_DESIGN = [
    "ARM", "NVDA", "AMD", "AVGO", "QCOM", "MRVL", "INTC", "SMCI",
]

# Top ETFs
TOP_ETFS = [
    "QQQ", "VOO", "VTI", "SPY", "IVV", "VUG", "SCHG", "VGT", "SMH", "SOXX",
    "BOTZ", "URA", "QTUM", "IWM", "IWF", "GLD", "IAU", "TLT", "HYG", "LQD",
    "XLK", "XLE", "XLF", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLC",
    "ARKK", "ARKG", "ARKW", "ARKF", "ARKQ", "SCHD", "VNQ", "VEA", "VWO", "EFA", "EEM",
    "IEFA", "IEMG", "AGG", "BND", "VCIT", "VIG", "USMV", "SPDW", "SPEM",
    "CIBR", "HACK", "BUG", "WCLD", "CLOU", "IPAY", "FINX",
    "JETS", "ROBO", "DRIV", "KARS", "BETZ",
    "IBB", "XBI", "PBE", "BBH",
    "REMX", "LIT", "COPX", "SIL", "GDX", "GDXJ",
    "TAN", "ICLN", "QCLN", "FAN", "GRID",
    "SHLD", "ITA", "XAR", "UFO", "ARKX",
    "AIQ", "CHAT",
]

# Crypto — all Alpaca-supported pairs (unsupported ones silently skipped)
CRYPTOS = [
    # Layer 1 majors
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "ADA/USD", "AVAX/USD",
    "DOGE/USD", "DOT/USD", "ATOM/USD", "ALGO/USD", "LTC/USD", "BCH/USD",
    # AI + Compute
    "RNDR/USD", "FET/USD", "NEAR/USD", "TAO/USD", "AGIX/USD", "OCEAN/USD",
    "AKT/USD", "WLD/USD",
    # Layer 1 — newer
    "SUI/USD", "APT/USD", "SEI/USD", "HBAR/USD", "ICP/USD", "EGLD/USD",
    # DeFi / Infrastructure
    "LINK/USD", "UNI/USD", "AAVE/USD", "MKR/USD", "CRV/USD", "LDO/USD",
    "JUP/USD", "RAY/USD", "PYTH/USD", "PENDLE/USD",
    # Layer 2 / Scaling
    "MATIC/USD", "ARB/USD", "OP/USD", "STRK/USD", "TIA/USD", "MNT/USD",
    "LRC/USD", "ZK/USD",
    # Gaming / Metaverse
    "IMX/USD", "GALA/USD", "SAND/USD", "MANA/USD", "AXS/USD", "ENJ/USD",
    "RON/USD", "APE/USD",
    # Meme coins
    "SHIB/USD", "PEPE/USD", "BONK/USD", "WIF/USD", "FLOKI/USD",
    # RWA / Finance
    "ONDO/USD", "ENA/USD", "OM/USD", "DYDX/USD", "GMX/USD",
    # Exchange tokens
    "CRO/USD",
    # Privacy / Specialized
    "XMR/USD", "ZEC/USD", "MINA/USD", "AR/USD", "FIL/USD",
    "THETA/USD", "HNT/USD", "CHZ/USD", "VET/USD", "QNT/USD",
    "XLM/USD",
    # Infrastructure
    "GRT/USD", "BAT/USD",
]


def _all_stocks() -> list[str]:
    combined = (
        QQQ_HOLDINGS + SMH_HOLDINGS + VGT_HOLDINGS + BOTZ_HOLDINGS +
        URA_HOLDINGS + QTUM_HOLDINGS + SCHG_HOLDINGS + ELITE_STOCKS +
        SP500_FINANCIALS + SP500_HEALTHCARE + SP500_ENERGY +
        SP500_INDUSTRIALS + SP500_CONSUMER + MOMENTUM_STOCKS +
        POWER_INFRA + CYBERSECURITY + ROBOTICS + DEFENSE + SPACE +
        CRYPTO_INFRA_STOCKS + AI_SOFTWARE + CHIP_DESIGN
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
                        "symbol":      sym,
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
    etfs   = list(dict.fromkeys(TOP_ETFS))
    all_stocks_etfs = list(dict.fromkeys(stocks + etfs))

    print(f"Scanning {len(all_stocks_etfs)} stocks/ETFs...")
    return _scan_symbols(all_stocks_etfs, fetch_daily_bars)
