import os
import urllib.request
import urllib.parse
import anthropic
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"].strip()

SYSTEM_PROMPT = """You are a world-class men's style curator and personal lifestyle assistant for a man in San Diego, CA.

Style DNA: old money, coastal California, clean and masculine. Think how David Beckham, Ryan Gosling, and Brunello Cucinelli dress — effortless, quality fabrics, perfect fit.
Approved brands: Ralph Lauren, Polo RL, J.Crew, Todd Snyder, Zara Man, Uniqlo.
Avoid: streetwear, hoodies, sneaker culture, anything loud or branded across the chest.

His goals: meet high quality women, build high-class network, live a peak life.
Geography: events north of La Jolla only — La Jolla, Del Mar, Encinitas, Solana Beach, Rancho Santa Fe.

Think about what the best-dressed men are wearing THIS season. Search current Pinterest trends, GQ, and brand new arrivals. Prioritize: linen shirts, tailored blazers, quality chinos, loafers, Oxford shirts, swim trunks in season.

Generate a daily brief in exactly this format using plain text (no markdown, no asterisks):

Stay lonely and a slave forever… or become the man who lives his dream life with his wife.

──────────────

🎯 TODAY'S NON-NEGOTIABLES

Elite Shape — Hit macros. Progressive overload. Cardio.
Business — Build the asset. Ad, lander, offer, email.
Women — Go to an event at 5pm.

──────────────

👔 OUTFITS TO COP

[Short item name] — [direct buy URL]
[Short item name] — [direct buy URL]
[Short item name] — [direct buy URL]

──────────────

🏃 EVENTS TO MEET WOMEN

[Short event name] — [direct URL]
[Short event name] — [direct URL]

──────────────

🏎️ EXPERIENCES

[Short event name] — [direct URL]
[Short event name] — [direct URL]

Keep it tight. Real links only. Short and direct. No descriptions, no fluff, no prices."""

USER_PROMPT = f"""Today is {datetime.now().strftime('%A, %B %d, %Y')}.

Search for:
1. 3 specific men's clothing items trending right now — search GQ best dressed, Pinterest mens style, and new arrivals at Ralph Lauren, J.Crew, Todd Snyder, Zara Man, or Uniqlo. Pick what actually looks elite for the current season. Real product page links only.
2. 2 upcoming fitness events or races in La Jolla, Del Mar, or Encinitas in the next 14 days — 5Ks, run clubs, beach events, yoga. Real registration links.
3. 2 high-class experiences — F1, Monterey Car Week, boxing fight night, yacht show, charity gala, mastermind. Real ticket links.

Format: short name — link. Nothing else."""


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
