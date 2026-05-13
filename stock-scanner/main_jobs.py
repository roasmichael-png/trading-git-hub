"""Weekly Job Postings Scanner — QQQ companies via Adzuna API."""
import os
import time
import requests
from datetime import date
from scanner.telegram import send_telegram
import config

ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

QQQ_COMPANIES = {
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "NVDA":  "NVIDIA",
    "AMZN":  "Amazon",
    "META":  "Meta",
    "GOOGL": "Google",
    "TSLA":  "Tesla",
    "AVGO":  "Broadcom",
    "COST":  "Costco",
    "NFLX":  "Netflix",
    "TMUS":  "T-Mobile",
    "AMD":   "AMD",
    "PEP":   "PepsiCo",
    "CSCO":  "Cisco",
    "ADBE":  "Adobe",
    "INTU":  "Intuit",
    "CMCSA": "Comcast",
    "TXN":   "Texas Instruments",
    "AMGN":  "Amgen",
    "QCOM":  "Qualcomm",
    "ISRG":  "Intuitive Surgical",
    "AMAT":  "Applied Materials",
    "BKNG":  "Booking Holdings",
    "MU":    "Micron Technology",
    "LRCX":  "Lam Research",
    "REGN":  "Regeneron",
    "KLAC":  "KLA Corporation",
    "MELI":  "MercadoLibre",
    "MDLZ":  "Mondelez",
    "PANW":  "Palo Alto Networks",
    "SNPS":  "Synopsys",
    "CDNS":  "Cadence Design",
    "CRWD":  "CrowdStrike",
    "FTNT":  "Fortinet",
    "ADI":   "Analog Devices",
    "MRVL":  "Marvell Technology",
    "ABNB":  "Airbnb",
    "ORLY":  "O'Reilly Auto Parts",
    "CHTR":  "Charter Communications",
    "WDAY":  "Workday",
    "NXPI":  "NXP Semiconductors",
    "PYPL":  "PayPal",
    "DXCM":  "Dexcom",
    "BIIB":  "Biogen",
    "IDXX":  "IDEXX Laboratories",
    "VRTX":  "Vertex Pharmaceuticals",
    "ADP":   "ADP",
    "GILD":  "Gilead Sciences",
    "PAYX":  "Paychex",
    "TEAM":  "Atlassian",
    "ODFL":  "Old Dominion Freight",
    "GEHC":  "GE HealthCare",
    "VRSK":  "Verisk Analytics",
    "ON":    "ON Semiconductor",
    "CSGP":  "CoStar Group",
    "ZS":    "Zscaler",
    "SBUX":  "Starbucks",
    "DLTR":  "Dollar Tree",
    "ROST":  "Ross Stores",
    "FAST":  "Fastenal",
    "BKR":   "Baker Hughes",
    "XEL":   "Xcel Energy",
    "CTSH":  "Cognizant",
    "PCAR":  "PACCAR",
    "WBD":   "Warner Bros Discovery",
    "ALGN":  "Align Technology",
    "ILMN":  "Illumina",
    "ZM":    "Zoom",
    "DDOG":  "Datadog",
    "TTD":   "The Trade Desk",
    "ENPH":  "Enphase Energy",
    "MRNA":  "Moderna",
    "CEG":   "Constellation Energy",
    "CPRT":  "Copart",
    "TTWO":  "Take-Two Interactive",
    "ROP":   "Roper Technologies",
    "CSX":   "CSX Corporation",
    "MCHP":  "Microchip Technology",
    "ANSS":  "ANSYS",
    "KDP":   "Keurig Dr Pepper",
    "EXC":   "Exelon",
    "GFS":   "GlobalFoundries",
    "RIVN":  "Rivian",
    "LCID":  "Lucid Motors",
    "HON":   "Honeywell",
    "PDD":   "PDD Holdings",
    "CDW":   "CDW Corporation",
    "CTAS":  "Cintas",
    "AEP":   "American Electric Power",
    "LULU":  "lululemon",
    "EBAY":  "eBay",
}


def get_job_count(company_name: str) -> int:
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id":           ADZUNA_APP_ID,
        "app_key":          ADZUNA_APP_KEY,
        "what_company":     company_name,
        "results_per_page": 1,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("count", 0)
    except Exception as e:
        print(f"  {company_name}: error — {e}")
        return -1


def run_jobs_scan() -> list[dict]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("ERROR: ADZUNA_APP_ID or ADZUNA_APP_KEY not set.")
        return []

    results = []
    total = len(QQQ_COMPANIES)
    for i, (ticker, name) in enumerate(QQQ_COMPANIES.items(), 1):
        print(f"  [{i}/{total}] {ticker} ({name})...", end=" ", flush=True)
        count = get_job_count(name)
        print(count if count >= 0 else "error")
        if count >= 0:
            results.append({"ticker": ticker, "company": name, "jobs": count})
        time.sleep(0.4)  # stay well under rate limit

    results.sort(key=lambda x: x["jobs"], reverse=True)
    return results


if __name__ == "__main__":
    print(f"QQQ Job Postings Scanner — {date.today().strftime('%b %d, %Y')}")
    print(f"Scanning {len(QQQ_COMPANIES)} companies...\n")

    results = run_jobs_scan()

    if not results:
        print("No results returned.")
    else:
        print(f"\n{'='*55}")
        print(f"  QQQ JOB POSTINGS — {date.today().strftime('%b %d, %Y')}")
        print(f"{'='*55}")
        print(f"{'TICKER':<7} {'COMPANY':<32} {'JOBS':>8}")
        print(f"{'-'*55}")
        for r in results:
            print(f"{r['ticker']:<7} {r['company']:<32} {r['jobs']:>8,}")

    if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
        today = date.today().strftime("%b %d")
        if not results:
            msg = f"QQQ Job Postings - {today}\n\nNo data returned."
        else:
            lines = [f"QQQ Job Postings - {today}", f"{len(results)} companies\n"]
            for r in results:
                lines.append(f"{r['ticker']:<6} {r['jobs']:>6,}  {r['company']}")
            msg = "\n".join(lines)
        send_telegram(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, msg)
