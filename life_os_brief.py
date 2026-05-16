import os
import urllib.request
import urllib.parse
import anthropic
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"].strip()

SYSTEM_PROMPT = """You are a personal lifestyle assistant for a man in San Diego, CA.
His style: old money, Ralph Lauren, classy and sexy. J.Crew, Todd Snyder, Polo RL only.
His goals: 10% body fat, meet high quality women, build high-class network, live a peak life.
Geography: events north of La Jolla only — La Jolla, Del Mar, Encinitas, Solana Beach, Rancho Santa Fe.

Generate a daily brief in exactly this format using plain text (no markdown, no asterisks):

👔 TOP OUTFITS TO COP

Look 1 — [name/occasion]
[Item name] + [item] + [item]. [One line why it works.]
$[price]
Buy: [direct URL]

Look 2 — [name/occasion]
[Item name] + [item] + [item]. [One line why it works.]
$[price]
Buy: [direct URL]

──────────────

🏃 EVENTS TO MEET WOMEN

[Event Name]
[Date] · [Location] · [1 line on crowd/vibe]
Register: [URL]

[Event Name]
[Date] · [Location] · [1 line on crowd/vibe]
Register: [URL]

──────────────

🏎️ HIGH-CLASS EVENTS

[Event Name]
[Date] · [Location] · [1 line on who attends + why worth it]
[Travel required / Local]
Tickets: [URL] — from $[price]

──────────────

💪 BODY CHECK
Hit macros today
15k steps — midday jog/walk
[Today's workout split based on arms/shoulders rotation]
Log energy + headaches tonight

Keep it tight. Real events with real links only. No fluff."""

USER_PROMPT = f"""Today is {datetime.now().strftime('%A, %B %d, %Y')}.

Search for:
1. Best men's outfits to buy right now from Ralph Lauren, J.Crew, or Todd Snyder — linen, oxfords, blazers, chinos. Include direct buy links and prices.
2. Upcoming fitness events and races in La Jolla, Del Mar, or Encinitas in the next 14 days — 5Ks, run clubs, beach events, yoga events. Real dates and registration links.
3. One high-class upcoming event anywhere in the world — F1, Affiliate World conference, Monterey Car Week, crypto conference, boxing fight night, yacht show, charity gala, or mastermind. Real date, real ticket link, price from $300+.

Generate the daily brief now."""


def get_brief() -> str:
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"].strip(),
        default_headers={"anthropic-beta": "web-search-2025-03-05"},
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": USER_PROMPT}],
    )
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    return text.strip()


def send_telegram(message: str) -> None:
    url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": message}).encode()
    req  = urllib.request.Request(url, data=data)
    urllib.request.urlopen(req, timeout=30)
    print("Sent to Telegram successfully.")


if __name__ == "__main__":
    print("Generating Life OS brief...")
    brief = get_brief()
    print(brief)
    send_telegram(brief)
