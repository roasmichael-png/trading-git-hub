import os
import time
import urllib.request
import urllib.parse
import anthropic
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"].strip()

_now = datetime.now()
_is_sunday = _now.weekday() == 6
_today = _now.strftime("%A, %B %d, %Y")

SUNDAY_BLOCK_TOP = """──────────────

📋 SUNDAY RESETS

Meal prep
<a href="https://www.livethelindley.com/floor-plans/">The Lindley — Studio ocean view</a>
<a href="https://www.youtube.com/watch?v=BBz-Jyr23M4&t=796s">Guitar practice</a>
<a href="https://www.ltfsd.com/">Pilot license — LTFSD</a>

──────────────

📓 JOURNAL (voice memo while walking)

1. What's the one thing I need to stop doing?
2. Where did I show up as the man I want to be this week?
3. What would my future wife think of how I spent this week?
4. What's the one business move that actually moves the needle?
5. Who do I need to reach out to?"""

HEADER = """Stay lonely and a slave forever… or become the man who lives his dream life with his wife.

──────────────

🎯 TODAY'S NON-NEGOTIABLES

Elite Shape — Hit macros. Progressive overload. Cardio.
Business — Build the asset. Ad, lander, offer, email.
Women — Go to an event at 5pm.

──────────────"""


def _call_claude(prompt: str, max_tokens: int = 800) -> str:
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"].strip(),
        default_headers={"anthropic-beta": "web-search-2025-03-05"},
    )
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
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
                wait = 65 * (attempt + 1)
                print(f"Rate limit hit, waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
            else:
                raise


def get_outfits() -> str:
    prompt = f"""Today is {_today}. San Diego men's style.

Search GQ, Pinterest mens style, and new arrivals at Ralph Lauren, J.Crew, Todd Snyder, Zara Man, or Uniqlo. Find 3 specific clothing items trending right now for the current season. Old money style: think Beckham, Gosling.

Output ONLY this block, nothing else:

👔 OUTFITS TO COP
<a href="[real product URL]">[Item name]</a>
<a href="[real product URL]">[Item name]</a>
<a href="[real product URL]">[Item name]</a>

Real product page links only. No prices. No descriptions. HTML anchor tags only."""
    return _call_claude(prompt, max_tokens=400)


def get_events() -> str:
    prompt = f"""Today is {_today}. San Diego, CA.

Search for:
1. 3 upcoming events to meet high-class women in San Diego in the next 14 days — prioritize Tango's San Diego dance nights, upscale salsa/bachata socials, rooftop events, charity galas, La Jolla art openings, Del Mar wine events, beach yoga La Jolla. No low-end bars. Search "Tango's San Diego events", "upscale salsa San Diego", "La Jolla social events".
2. 2 high-class experiences OR entrepreneur/founder networking events — F1, boxing fight night, charity gala, founder mastermind, YPO event, entrepreneur conference San Diego. Real ticket links.

Output ONLY these two blocks, nothing else:

🏃 EVENTS TO MEET WOMEN
<a href="[real URL]">[Event name]</a>
<a href="[real URL]">[Event name]</a>
<a href="[real URL]">[Event name]</a>

──────────────

🏎️ EXPERIENCES & NETWORK
<a href="[real URL]">[Event name]</a>
<a href="[real URL]">[Event name]</a>

HTML anchor tags only. Real links only. No descriptions."""
    return _call_claude(prompt, max_tokens=400)


def get_sunday_extras() -> str:
    prompt = f"""Today is {_today}.

Search for:
1. 4 viral men's Instagram/Hinge photo ideas right now — search "men's instagram content ideas that attract women 2025", "husband material social media posts men". Specific shoot concepts showing adventure, ambition, warmth, strength. One line each (e.g. "Golden hour solo hike shot from behind on trail").
2. 4 thoughtful gifts — one each for: a dad who loves Ferraris, a grandma who loves cooking, a 1-year-old goddaughter, a friend focused on business growth. Search "most thoughtful gifts 2025". Real specific products with purchase links.

Output ONLY these two blocks:

──────────────

📸 CONTENT TO SHOOT THIS WEEK

· [Specific shoot idea]
· [Specific shoot idea]
· [Specific shoot idea]
· [Specific shoot idea]

──────────────

🎁 GIFTS TO SEND THIS WEEK

· Dad: <a href="[product URL]">[Gift name]</a>
· Grandma: <a href="[product URL]">[Gift name]</a>
· Goddaughter: <a href="[product URL]">[Gift name]</a>
· Friend: <a href="[product URL]">[Gift name]</a>"""
    return _call_claude(prompt, max_tokens=500)


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
    print("Generating outfits...")
    outfits = get_outfits()

    print("Waiting 65s before next API call to avoid rate limit...")
    time.sleep(65)

    print("Generating events...")
    events = get_events()

    sunday_extras = ""
    if _is_sunday:
        print("Waiting 65s before Sunday extras...")
        time.sleep(65)
        print("Generating Sunday extras...")
        sunday_extras = get_sunday_extras()

    # Assemble brief
    parts = [HEADER, outfits, "\n──────────────\n", events]
    if _is_sunday:
        parts.insert(0, SUNDAY_BLOCK_TOP + "\n\n──────────────\n")
        if sunday_extras:
            parts.append("\n" + sunday_extras)

    brief = "\n".join(parts)
    print(brief)
    send_telegram(brief)
