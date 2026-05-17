import os
import json
import urllib.request
import urllib.parse
import anthropic
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"].strip()

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results", "scanner_results.json")

THOUGHT_LEADERS = [
    "Elon Musk", "Jensen Huang", "Sam Altman", "Peter Thiel",
    "Marc Andreessen", "Naval Ravikant", "Warren Buffett",
    "Stan Druckenmiller", "Howard Marks", "Jeff Bezos",
    "Bill Ackman", "Ray Dalio", "Cathie Wood",
    "Jerome Powell", "Donald Trump",
]


def load_scanner_hits() -> list[dict]:
    try:
        with open(RESULTS_PATH) as f:
            data = json.load(f)
        all_hits = (
            data.get("scanner1", []) +
            data.get("scanner2", []) +
            data.get("scanner3", [])
        )
        seen = {}
        for h in all_hits:
            sym = h["symbol"]
            if sym not in seen or h.get("rating") == "STRONG BUY":
                seen[sym] = h
        return list(seen.values())
    except Exception as e:
        print(f"Could not load scanner results: {e}")
        return []


def build_report(hits: list[dict]) -> str:
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"].strip(),
        default_headers={"anthropic-beta": "web-search-2025-03-05"},
    )

    symbols = [h["symbol"] for h in hits[:8]]
    leaders_str = ", ".join(THOUGHT_LEADERS)
    hits_str = ", ".join(symbols) if symbols else "No scanner hits today — still run all sections"

    prompt = f"""Today is {datetime.now().strftime('%A, %B %d, %Y')}. Pre-market. You are a macro strategist, intelligence analyst, and capital allocator.

Scanner hits from yesterday to research: {hits_str}

Search the web thoroughly and produce a GLOBAL INTELLIGENCE REPORT with exactly these 6 sections. Keep every line short — one line max per item. Use HTML anchor tags for any links. No markdown, no asterisks, plain text only.

──────────────────────────────────────
🌎 GLOBAL INTELLIGENCE REPORT — {datetime.now().strftime('%b %d, %Y')}
──────────────────────────────────────

SECTION 1 — MARKET SETUP
Search current pre-market futures and overnight levels.

SPY: [pre-market price and % change]
QQQ: [pre-market price and % change]
BTC: [current price and % change]
Futures: [S&P and Nasdaq futures direction]
VIX: [level — low/normal/elevated/fear]
Strongest sector today: [sector name and why]
Weakest sector today: [sector name and why]
Unusual options: [any large unusual options activity spotted today]

──────────────────────────────────────

SECTION 2 — MACRO THREATS
Search today's biggest macro risks globally.

Wars/Geopolitics: [one line on biggest active conflict or tension affecting markets]
Oil: [price and what's driving it]
China/Taiwan: [any tension, trade, or policy update]
Fed/Rates: [current stance, any speeches or signals this week]
Inflation: [latest CPI or PCE reading and direction]
Supply Chain: [any disruption worth watching]
Wild card: [one macro risk most people are ignoring right now]

──────────────────────────────────────

SECTION 3 — SMART MONEY
Search SEC Form 4 filings, congressional trades, hedge fund moves.

Insider buys this week: [Executive — Company — $amount — date]
Insider buys this week: [Executive — Company — $amount — date]
Congress trades: [Senator/Rep — stock bought/sold — this week]
Hedge fund move: [fund name — position change — this week]
Analyst upgrade: [Stock — firm — new price target]
Analyst upgrade: [Stock — firm — new price target]
unusual_whales signal: [any notable options or congressional alert today]

For scanner hits {hits_str} — check each for recent CEO/CFO Form 4 buys.

──────────────────────────────────────

SECTION 4 — FUTURE TRENDS
Search what is accelerating RIGHT NOW in each sector.

AI: [biggest AI development or shift this week]
Robotics: [key move — company, product, or deal]
Biotech: [biggest FDA, trial, or breakthrough news]
Defense: [contract, conflict, or budget news driving stocks]
Nuclear: [SMR, uranium, or energy policy update]
Crypto: [BTC/ETH trend + any regulatory or institutional move]
Energy: [oil, solar, or grid infrastructure news]
Space: [launch, contract, or milestone this week]

──────────────────────────────────────

SECTION 5 — THOUGHT LEADERS
Search what each of these people said or did in the last 7 days: {leaders_str}

For each one that has something relevant and actionable, write:
[Name]: [one line — what they said, did, or invested in]

Then end with:
🔮 WHAT THE SMARTEST PEOPLE ARE SEEING RIGHT NOW:
[2-3 sentence synthesis — what is the consensus view among the sharpest minds globally? What are they positioning for? What risk are they all quietly watching?]

──────────────────────────────────────

SECTION 6 — TODAY'S TRADES
For each scanner hit, give a fast verdict.

[SYMBOL] — [RATING] — [SECTOR]
News: [one line]
Insider: [bought X shares DATE — or None]
Verdict: BUY / WAIT / SKIP and one line why

──────────────────────────────────────

Keep it tight, factual, and actionable. You are writing for someone who wants to think like a capital allocator and intelligence analyst, not a day trader."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    return text.strip()


def send_telegram(message: str) -> None:
    max_len = 4000
    chunks = [message[i:i+max_len] for i in range(0, len(message), max_len)]
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chunk in chunks:
        data = urllib.parse.urlencode({
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       chunk,
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=30)
    print(f"Sent {len(chunks)} message(s) to Telegram.")


if __name__ == "__main__":
    print("Running Global Intelligence Report...")
    hits = load_scanner_hits()
    print(f"Found {len(hits)} scanner hits.")
    report = build_report(hits)
    print(report)
    send_telegram(report)
