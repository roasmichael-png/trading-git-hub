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

    prompt = f"""Today is {datetime.now().strftime('%A, %B %d, %Y')}. Pre-market intelligence briefing.

Scanner hits to research: {hits_str}

Search the web. Return a punchy briefing — every line is ONE bullet. No paragraphs. No sentences longer than 10 words. Think Bloomberg terminal meets military briefing. Plain text, HTML anchor tags for links only.

🌎 GLOBAL INTEL — {datetime.now().strftime('%b %d')}

━━━ MARKET
SPY: $X (±X%)
QQQ: $X (±X%)
BTC: $X (±X%)
VIX: X — [calm/watch/fear]
Hot: [sector]
Cold: [sector]
Options: [unusual activity or "quiet"]

━━━ MACRO THREATS
[Topic]: [max 8 words]
[Topic]: [max 8 words]
[Topic]: [max 8 words]
[Topic]: [max 8 words]
⚠️ Wild Card: [max 8 words]

━━━ SMART MONEY
[Executive] bought $X in [Company] [date]
[Executive] bought $X in [Company] [date]
Congress: [Name] — [stock] — [bought/sold]
Upgrade: [Stock] — [Firm] — PT $X→$X
unusual_whales: [one line or "nothing notable"]

━━━ TRENDS ACCELERATING
AI: [max 8 words]
Defense: [max 8 words]
Nuclear: [max 8 words]
Crypto: [max 8 words]
Biotech: [max 8 words]
Space: [max 8 words]

━━━ WHAT THE SMARTEST PEOPLE ARE SAYING
Search {leaders_str} — only include those with news this week.
[Name]: [max 8 words]
[Name]: [max 8 words]
[Name]: [max 8 words]
🔮 Consensus: [max 12 words on what they're all positioning for]

━━━ TODAY'S TRADES
For each scanner hit: {hits_str}
[SYMBOL] [RATING] — [one line news] — Verdict: BUY/WAIT/SKIP

━━━ CLAUDE'S CALL
Buy: [top 2-3 sectors or stocks, 5 words each]
Avoid: [1-2 things, 5 words each]
Hidden opportunity: [max 10 words]
Top risk: [max 8 words]
Conviction pick this week: [SYMBOL] — [max 8 words why]"""

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
