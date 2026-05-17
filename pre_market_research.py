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
    # Billionaires / Builders
    "Elon Musk", "Jeff Bezos", "Bill Gates", "Warren Buffett",
    "Sam Altman", "Jensen Huang", "Peter Thiel", "Marc Andreessen",
    "Naval Ravikant", "Larry Ellison",
    # Tech CEOs
    "Satya Nadella", "Lisa Su AMD", "Sundar Pichai", "Mark Zuckerberg",
    # Macro / Politics
    "Donald Trump", "Jerome Powell Fed", "Ray Dalio",
    # Finance / Investing
    "Stan Druckenmiller", "Howard Marks", "Tom Lee Fundstrat",
    "Dan Ives Wedbush", "Michael Burry", "Paul Tudor Jones",
    "Cathie Wood ARK", "Mark Minervini", "unusual_whales",
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
        # dedupe by symbol, keep highest rated
        seen = {}
        for h in all_hits:
            sym = h["symbol"]
            if sym not in seen or h.get("rating") == "STRONG BUY":
                seen[sym] = h
        return list(seen.values())
    except Exception as e:
        print(f"Could not load scanner results: {e}")
        return []


def research(hits: list[dict]) -> str:
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"].strip(),
        default_headers={"anthropic-beta": "web-search-2025-03-05"},
    )

    symbols = [h["symbol"] for h in hits[:8]]  # cap at 8 to keep brief tight
    leaders_str = ", ".join(THOUGHT_LEADERS)

    if not symbols:
        symbols_section = "No scanner hits from yesterday — give a general market outlook instead."
    else:
        symbols_section = f"Scanner hits to research: {', '.join(symbols)}"

    prompt = f"""Today is {datetime.now().strftime('%A, %B %d, %Y')}. Pre-market is about to open.

{symbols_section}

Do the following:

1. For each scanner hit, search for:
   - Latest news in last 48 hours
   - Analyst upgrades, downgrades, or price target changes
   - Any upcoming earnings date
   - X/Twitter or StockTwits sentiment (bullish or bearish?)
   - SEC Form 4 insider filings — has any CEO, CFO, or C-suite bought or sold shares in the last 30 days? Search "[SYMBOL] insider buying SEC Form 4 2025" or check openinsider.com
   - One sentence on why smart money might be moving

2. Search what these world-class leaders are currently saying about the market, tech, AI, or any of these stocks: {leaders_str}. Pick the 3 most relevant and actionable. Include what they are personally investing in or building right now if known.

3. Check the macro calendar — any Fed events, CPI, jobs report, Trump policy moves, or major earnings this week that could move markets?

4. Any recent significant insider buys across the broader market this week — CEOs or executives buying their OWN stock with personal money (this is a strong signal). Search "biggest insider buys this week 2025".

Format the output like this (plain text, no markdown, use HTML only for links):

🌅 PRE-MARKET RESEARCH — {datetime.now().strftime('%b %d')}

──────────────
📊 SCANNER HITS

[SYMBOL] — [SECTOR] — [RATING]
News: [one line]
Analyst: [one line or "No change"]
Earnings: [X days out or "N/A"]
Insider: [CEO/CFO bought X shares on DATE — or "No recent filing"]
Sentiment: [Bullish / Neutral / Bearish]
Edge: [one line why this could move]

[repeat for each symbol]

──────────────
🏦 INSIDER BUYS THIS WEEK

[Company] — [Executive title] bought $[amount] on [date]
[Company] — [Executive title] bought $[amount] on [date]

──────────────
🧠 WORLD-CLASS VIEWS

[Name]: [one line on their current view or what they are buying/building]
[Name]: [one line]
[Name]: [one line]

──────────────
📅 MACRO THIS WEEK

[Event] — [Date] — [Why it matters in one line]

Keep everything short. One line per field. This is a quick read before the market opens."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    return text.strip()


def send_telegram(message: str) -> None:
    # Telegram has a 4096 char limit — split if needed
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
    print("Running pre-market research...")
    hits = load_scanner_hits()
    print(f"Found {len(hits)} scanner hits to research.")
    report = research(hits)
    print(report)
    send_telegram(report)
