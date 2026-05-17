"""
Kalshi Prediction Market Scanner
Finds mispriced markets, analyzes with Claude, sizes with Kelly Criterion.
"""
import os
import json
import time
import urllib.request
import urllib.parse
import anthropic
from datetime import datetime, timezone

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"].strip()

KALSHI_BASE = "https://api.kalshi.com/trade-api/v2"

# Only scan categories we care about
TARGET_CATEGORIES = [
    "economics", "finance", "crypto", "politics",
    "fed", "inflation", "markets", "geopolitics", "tech"
]

# Minimum volume to ensure liquidity
MIN_VOLUME = 5000

# Only look at markets resolving within 60 days
MAX_DAYS_TO_CLOSE = 60

# Max Kelly fraction — never bet more than 10% of bankroll on one market
MAX_KELLY = 0.10


def fetch_markets() -> list[dict]:
    """Fetch top open markets from Kalshi sorted by volume."""
    try:
        url = f"{KALSHI_BASE}/markets?status=open&limit=100"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        markets = data.get("markets", [])
    except Exception as e:
        print(f"Kalshi fetch failed: {e}")
        return []

    now = datetime.now(timezone.utc)
    good = []
    for m in markets:
        # Must have volume
        if m.get("volume", 0) < MIN_VOLUME:
            continue
        # Must close within MAX_DAYS_TO_CLOSE
        close_str = m.get("close_time", "")
        if close_str:
            try:
                close_dt = datetime.fromisoformat(close_str.replace("Z", "+00:00"))
                days_left = (close_dt - now).days
                if days_left < 0 or days_left > MAX_DAYS_TO_CLOSE:
                    continue
                m["days_left"] = days_left
            except Exception:
                continue
        # Must have a tradeable price
        yes_ask = m.get("yes_ask", 0)
        if yes_ask <= 0 or yes_ask >= 99:
            continue
        good.append(m)

    # Sort by volume descending, take top 20
    good.sort(key=lambda x: x.get("volume", 0), reverse=True)
    return good[:20]


def kelly(p_true: float, p_market: float, side: str) -> float:
    """
    Kelly Criterion fraction.
    side = 'yes' or 'no'
    Returns fraction of bankroll to bet (capped at MAX_KELLY).
    """
    if side == "yes":
        # Bet YES: win (1-p_market)/p_market for every $p_market risked
        b = (100 - p_market) / p_market
        q = 1 - p_true
        f = (b * p_true - q) / b
    else:
        # Bet NO: win p_market/(100-p_market)
        p_no_market = (100 - p_market) / 100
        b = p_market / (100 - p_market)
        p_no_true = 1 - p_true
        q = 1 - p_no_true
        f = (b * p_no_true - q) / b

    return max(0.0, min(f, MAX_KELLY))


def analyze_markets(markets: list[dict]) -> str:
    """Use Claude to estimate true probability for each market and find edge."""
    if not markets:
        return "No liquid markets found today."

    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"].strip(),
        default_headers={"anthropic-beta": "web-search-2025-03-05"},
    )

    market_lines = []
    for m in markets:
        p_mkt = m.get("yes_ask", 50)
        title = m.get("title", m.get("ticker", "?"))
        days = m.get("days_left", "?")
        vol = m.get("volume", 0)
        market_lines.append(
            f"- [{m.get('ticker')}] \"{title}\" | Market: {p_mkt}% YES | "
            f"Closes in {days} days | Volume: ${vol:,}"
        )

    markets_str = "\n".join(market_lines)
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Today is {today}. You are an expert prediction market analyst.

Here are active Kalshi prediction markets with their current market prices:

{markets_str}

For each market:
1. Search the web for the latest news and data relevant to this question
2. Estimate the TRUE probability of YES resolving (based on your research)
3. Calculate the EDGE = your probability minus market probability
4. Only flag markets where |edge| >= 10 percentage points — that's where real mispricing exists

Then output ONLY the top 3-5 best opportunities in this exact format (plain text, HTML links ok):

🎯 PREDICTION MARKET EDGE — {today}

──────────────

[Market title — plain English]
Market price: [X]% YES
Your estimate: [X]% YES
Edge: +[X]% (BUY YES) or -[X]% (BUY NO)
Why: [one line — what the market is getting wrong]
Bet: [YES or NO]
Kelly size: [X]% of bankroll
Closes: [X] days

──────────────

[repeat for each opportunity]

──────────────

⚠️ PASS LIST (no edge):
[ticker]: market fairly priced at [X]%

If fewer than 3 markets have real edge, say so — don't force picks.
Keep it short. One line per field. No paragraphs."""

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": prompt}],
            )
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            return text.strip()
        except anthropic.RateLimitError:
            if attempt < 2:
                print(f"Rate limit, waiting 60s...")
                time.sleep(60)
            else:
                raise


def send_telegram(message: str) -> None:
    max_len = 4000
    chunks = []
    current = ""
    for line in message.splitlines(keepends=True):
        if len(current) + len(line) > max_len:
            chunks.append(current.strip())
            current = line
        else:
            current += line
    if current.strip():
        chunks.append(current.strip())

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
    print("Fetching Kalshi markets...")
    markets = fetch_markets()
    print(f"Found {len(markets)} liquid markets to analyze.")

    print("Analyzing with Claude...")
    report = analyze_markets(markets)
    print(report)

    send_telegram(report)
