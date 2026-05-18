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

STYLE_CONTEXT = """The man: San Diego, mid-30s, old money aesthetic, athletic build. Style icons: David Beckham, Ryan Gosling, Glen Powell. Budget: mid-to-high. Brands that fit: Ralph Lauren, J.Crew, Todd Snyder, Zara Man, Uniqlo premium line, Banana Republic, Billy Reid, Faherty, Vince, Club Monaco. NO streetwear, NO hoodies, NO sneaker culture. Think: linen shirts, tailored chinos, leather loafers, quality denim, blazers, polo shirts. Must look like money without trying."""


def _call_claude(prompt: str, max_tokens: int = 1000) -> str:
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
    prompt = f"""Today is {_today}.

{STYLE_CONTEXT}

Search RIGHT NOW for specific in-stock men's clothing items. Search these exact queries:
- "Ralph Lauren new arrivals {_now.strftime('%B %Y')}"
- "Todd Snyder men's new arrivals"
- "J.Crew men's best sellers"
- "Zara man new collection {_now.strftime('%Y')}"
- "GQ best dressed men {_now.strftime('%B %Y')}"

Find 3 SPECIFIC items that are:
1. Actually available to buy today (real product pages, not articles)
2. Season-appropriate for San Diego right now ({_now.strftime('%B')})
3. Elevated and specific — not generic "white button-down" but "Ralph Lauren Slim Fit Linen Oxford in Coastal Blue"
4. Linkable directly to the product page

Output ONLY this block — no intro, no explanation:

👔 OUTFITS TO COP

<a href="[direct product URL]">[Brand — Specific item name and color]</a>
<a href="[direct product URL]">[Brand — Specific item name and color]</a>
<a href="[direct product URL]">[Brand — Specific item name and color]</a>

──────────────"""
    return _call_claude(prompt, max_tokens=600)


def get_events() -> str:
    prompt = f"""Today is {_today}. Location: San Diego, CA (La Jolla, Del Mar, Little Italy, Gaslamp area).

Search for REAL upcoming events happening in the next 14 days. Search these exact queries:
- "Tango's San Diego upcoming events {_now.strftime('%B %Y')}"
- "salsa dancing San Diego {_now.strftime('%B %Y')}"
- "bachata social San Diego {_now.strftime('%B %Y')}"
- "La Jolla art opening gala {_now.strftime('%B %Y')}"
- "San Diego rooftop event {_now.strftime('%B %Y')}"
- "Del Mar wine tasting {_now.strftime('%B %Y')}"
- "San Diego charity gala {_now.strftime('%B %Y')}"
- "entrepreneur networking San Diego {_now.strftime('%B %Y')}"
- "YPO San Diego event"
- "founder mastermind San Diego"

RULES:
- Events must have a real URL to buy tickets or register
- Events should attract high-quality, ambitious people (not college bars, not dive bars)
- Dance events (salsa, bachata, tango) are TOP priority — sophisticated crowd, great for meeting women
- Rooftop bars with events, wine tastings, art galas are great
- Charity events, networking with executives/founders are great

Output ONLY these two blocks — no intro, no explanation:

🏃 EVENTS TO MEET WOMEN

<a href="[real ticket/event URL]">[Specific event name — Day, Date]</a>
<a href="[real ticket/event URL]">[Specific event name — Day, Date]</a>
<a href="[real ticket/event URL]">[Specific event name — Day, Date]</a>

──────────────

🏎️ EXPERIENCES & NETWORK

<a href="[real URL]">[Specific event name — Day, Date]</a>
<a href="[real URL]">[Specific event name — Day, Date]</a>

──────────────"""
    return _call_claude(prompt, max_tokens=700)


def get_sunday_extras() -> str:
    prompt = f"""Today is {_today}.

{STYLE_CONTEXT}

Search for:

PART 1 — Photo ideas:
Search "men's instagram content ideas 2025 attract women", "what photos make men look husband material instagram", "men hinge photo ideas that get matches 2025".
Find 4 SPECIFIC shoot concepts — not generic. Think: exact location type, lighting, outfit, activity. The man is athletic, has old money style, based in San Diego. He surfs, hikes, dresses well, builds businesses.
Examples of the specificity I want: "Golden hour on Torrey Pines trail, shot from behind, linen shirt, looking out at the ocean" or "Sitting at a marble cafe table reading WSJ, navy blazer, espresso in hand, shot candidly"

PART 2 — Gifts:
Search for specific thoughtful gifts for:
- A dad who loves Ferraris (find a real luxury/experiential gift — Ferrari experience, artwork, high-end auto accessory)
- A grandma who loves cooking (find a specific high-end kitchen item or experience — not generic "cookbook")
- A 1-year-old goddaughter (find something meaningful, heirloom quality)
- A friend laser-focused on business growth (find a specific book, tool, experience, or resource that actually moves the needle)

Search "most thoughtful luxury gifts 2025", "best gifts for [category] 2025". Real products with real purchase links.

Output ONLY:

──────────────

📸 CONTENT TO SHOOT THIS WEEK

· [Very specific shoot concept with location, lighting, outfit, activity]
· [Very specific shoot concept with location, lighting, outfit, activity]
· [Very specific shoot concept with location, lighting, outfit, activity]
· [Very specific shoot concept with location, lighting, outfit, activity]

──────────────

🎁 GIFTS TO SEND THIS WEEK

· Dad: <a href="[product URL]">[Specific gift name]</a>
· Grandma: <a href="[product URL]">[Specific gift name]</a>
· Goddaughter: <a href="[product URL]">[Specific gift name]</a>
· Friend: <a href="[product URL]">[Specific gift name]</a>"""
    return _call_claude(prompt, max_tokens=800)


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
    parts = []

    if _is_sunday:
        parts.append(SUNDAY_BLOCK_TOP + "\n\n──────────────")

    parts.append(HEADER)

    print("Generating outfits...")
    outfits = get_outfits()
    parts.append(outfits)

    print("Waiting 65s before events call...")
    time.sleep(65)

    print("Generating events...")
    events = get_events()
    parts.append(events)

    if _is_sunday:
        print("Waiting 65s before Sunday extras...")
        time.sleep(65)
        print("Generating Sunday extras...")
        sunday_extras = get_sunday_extras()
        parts.append(sunday_extras)

    brief = "\n\n".join(parts)
    print(brief)
    send_telegram(brief)
