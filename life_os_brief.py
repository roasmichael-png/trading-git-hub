import os
import urllib.request
import urllib.parse
import anthropic
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"].strip()

_now = datetime.now()
_is_sunday = _now.weekday() == 6

SUNDAY_BLOCK = """
──────────────

📋 SUNDAY RESETS

<a href="https://www.livethelindley.com/floor-plans/">The Lindley — Studio ocean view</a>
<a href="https://www.youtube.com/watch?v=BBz-Jyr23M4&t=796s">Guitar practice</a>
<a href="https://www.ltfsd.com/">Pilot license — LTFSD</a>

Meal prep — proteins, rice, veggies for the week

📸 Hinge photos this week:
· Beach / outdoors candid
· Business setting (laptop, coffee, building)
· Travel or high-class venue
· Fitness / body shot

📱 Instagram content ideas:
· Holding a dog at the park
· Behind-the-scenes building something
· Travel or car shot
· Progress physique post

🎁 Gift ideas to send this week:
· Dad (Ferrari fan) — search "Ferrari fan gift" on <a href="https://www.amazon.com/s?k=ferrari+fan+gift+men">Amazon</a>
· Grandma (loves cooking) — search <a href="https://www.amazon.com/s?k=luxury+cooking+gift+grandma">Amazon cooking gifts</a>
· Goddaughter (1 yr old) — <a href="https://www.amazon.com/s?k=baby+girl+1+year+old+gift">Baby girl 1yr gifts</a>
· Friends — <a href="https://www.amazon.com/s?k=business+self+improvement+gift+men">Business/growth gifts</a>"""

SYSTEM_PROMPT = """You are a world-class men's style curator and personal lifestyle assistant for a man in San Diego, CA.

Style DNA: old money, coastal California, clean and masculine. Think how David Beckham, Ryan Gosling, and Brunello Cucinelli dress — effortless, quality fabrics, perfect fit.
Approved brands: Ralph Lauren, Polo RL, J.Crew, Todd Snyder, Zara Man, Uniqlo.
Avoid: streetwear, hoodies, sneaker culture, anything loud or branded across the chest.

His goals: meet high quality women, build elite network (entrepreneurs, founders, builders), live a peak life.
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

<a href="[direct buy URL]">[Short item name]</a>
<a href="[direct buy URL]">[Short item name]</a>
<a href="[direct buy URL]">[Short item name]</a>

──────────────

🏃 EVENTS TO MEET WOMEN

<a href="[direct URL]">[Short event name]</a>
<a href="[direct URL]">[Short event name]</a>

──────────────

🏎️ EXPERIENCES & NETWORK

<a href="[direct URL]">[Short event name]</a>
<a href="[direct URL]">[Short event name]</a>

Keep it tight. Real links only. Short and direct. No descriptions, no fluff, no prices. Output valid HTML anchor tags exactly as shown."""

USER_PROMPT = f"""Today is {_now.strftime('%A, %B %d, %Y')}.

Search for:
1. 3 specific men's clothing items trending right now — search GQ best dressed, Pinterest mens style, and new arrivals at Ralph Lauren, J.Crew, Todd Snyder, Zara Man, or Uniqlo. Pick what actually looks elite for the current season. Real product page links only.
2. 2 upcoming fitness events or races in La Jolla, Del Mar, or Encinitas in the next 14 days — 5Ks, run clubs, beach events, yoga. Real registration links.
3. 2 high-class experiences OR entrepreneur/founder networking events — F1, Monterey Car Week, boxing fight night, charity gala, ClickFunnels meetup, Shopify meetup, founder mastermind, YPO event, entrepreneur conference. Real ticket or registration links.

Format each item as an HTML anchor tag: <a href="URL">Short name</a>. Nothing else."""


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
    data = urllib.parse.urlencode({
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }).encode()
    req  = urllib.request.Request(url, data=data)
    urllib.request.urlopen(req, timeout=30)
    print("Sent to Telegram successfully.")


if __name__ == "__main__":
    print("Generating Life OS brief...")
    brief = get_brief()
    if _is_sunday:
        brief += SUNDAY_BLOCK
    print(brief)
    send_telegram(brief)
