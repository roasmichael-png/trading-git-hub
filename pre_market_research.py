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

    prompt = f"""Today is {datetime.now().strftime('%A, %B %d, %Y')}. Pre-market. You are a world-class macro strategist, intelligence analyst, and capital allocator with 30 years of experience managing billions.

Scanner hits from yesterday to research: {hits_str}

Search the web thoroughly. Produce a GLOBAL INTELLIGENCE REPORT with exactly these 7 sections. Use blank lines between every item for readability. No markdown, no asterisks, plain text only. Use HTML anchor tags for any links.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌎 GLOBAL INTELLIGENCE REPORT
{datetime.now().strftime('%A, %B %d, %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


━━━ SECTION 1 — MARKET SETUP ━━━

Search current pre-market futures and overnight data.

SPY: [price] ([%] pre-market)

QQQ: [price] ([%] pre-market)

BTC: [price] ([%])

Futures: [S&P and Nasdaq direction]

VIX: [level] — [low / normal / elevated / fear]

Strongest Sector: [name — one line why]

Weakest Sector: [name — one line why]

Unusual Options: [any notable sweep or unusual activity]


━━━ SECTION 2 — MACRO THREATS ━━━

Search today's biggest global risks.

Wars/Geopolitics: [one line]

Oil: [price and driver]

China/Taiwan: [latest update]

Fed/Rates: [current stance and this week's signals]

Inflation: [latest reading and direction]

Supply Chain: [any active disruption]

Wild Card: [the one risk most people are ignoring]


━━━ SECTION 3 — SMART MONEY ━━━

Search SEC Form 4 filings, congressional trades, hedge fund moves. Also check each scanner hit for CEO/CFO insider buys.

Insider Buy: [Executive — Company — $amount — date]

Insider Buy: [Executive — Company — $amount — date]

Congress Trade: [Senator/Rep — stock — bought or sold — date]

Hedge Fund: [fund — position change this week]

Analyst Upgrade: [Stock — firm — old PT → new PT]

Analyst Upgrade: [Stock — firm — old PT → new PT]

unusual_whales: [notable signal today]


━━━ SECTION 4 — FUTURE TRENDS ━━━

Search what is accelerating right now in each sector.

AI: [biggest shift this week]

Robotics: [key company, product, or deal]

Biotech: [FDA, trial, or breakthrough]

Defense: [contract, conflict, or budget news]

Nuclear: [SMR, uranium, or policy update]

Crypto: [trend + institutional or regulatory move]

Energy: [oil, solar, or grid news]

Space: [launch, contract, or milestone]


━━━ SECTION 5 — THOUGHT LEADERS ━━━

Search what each of these people said, did, or invested in during the last 7 days: {leaders_str}

Only include those with something relevant and actionable this week.

[Name]: [one line — what they said or where they are putting money]

[Name]: [one line]

[Name]: [one line]

🔮 CONSENSUS VIEW:
[2-3 sentences — what are the sharpest minds globally positioning for right now? What risk are they all quietly watching?]


━━━ SECTION 6 — TODAY'S TRADES ━━━

For each scanner hit give a fast verdict.

[SYMBOL] — [RATING] — [SECTOR]
News: [one line]
Insider: [bought X shares DATE — or None]
Verdict: BUY / WAIT / SKIP — [one line reason]


━━━ SECTION 7 — CLAUDE'S ANALYSIS ━━━

This is your own independent world-class view — not a summary of others. Think like a top fund manager allocating $10M today.

Based on everything above, give:

WHERE I WOULD PUT MONEY RIGHT NOW:
[3-5 specific sectors or stocks and exactly why — be direct and confident]

WHAT I AM AVOIDING AND WHY:
[2-3 things to stay away from with reasoning]

THE BIGGEST OPPORTUNITY MOST PEOPLE ARE MISSING:
[One contrarian or forward-looking thesis — think 6-18 months out]

THE BIGGEST RISK TO THIS PORTFOLIO:
[One honest macro or market risk that could break the thesis]

MY CONVICTION CALL THIS WEEK:
[One single highest-conviction idea — sector or stock — and why now]

Be bold. Be specific. This is the most important section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=5000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    return format_report(text.strip())


def format_report(text: str) -> str:
    """Enforce consistent spacing so Telegram renders cleanly."""
    import re
    lines = text.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        # Section headers get extra breathing room
        if stripped.startswith("━━━") or stripped.startswith("🌎"):
            if out and out[-1] != "":
                out.append("")
            out.append(stripped)
            out.append("")
        # Key-value lines (e.g. "SPY: ...") get a blank line after
        elif re.match(r'^[A-Z][A-Za-z /]+:', stripped) and stripped:
            out.append(stripped)
            out.append("")
        # Emoji bullets stay as-is with spacing
        elif stripped.startswith(("🔮", "WHERE", "WHAT I AM", "THE BIGGEST", "MY CONVICTION")):
            if out and out[-1] != "":
                out.append("")
            out.append(stripped)
            out.append("")
        elif stripped:
            out.append(stripped)
        else:
            # Collapse multiple blank lines into one
            if out and out[-1] != "":
                out.append("")
    # Remove leading/trailing blank lines
    while out and out[0] == "":
        out.pop(0)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def send_telegram(message: str) -> None:
    max_len = 4000
    # Split cleanly on blank lines so we don't cut mid-section
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
    print("Running Global Intelligence Report...")
    hits = load_scanner_hits()
    print(f"Found {len(hits)} scanner hits.")
    report = build_report(hits)
    print(report)
    send_telegram(report)
