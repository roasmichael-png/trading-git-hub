"""Daily Life OS Briefing — San Diego weather, outfit, events, networking."""
import os
import urllib.request
import urllib.parse
import requests
import anthropic
from datetime import datetime


def get_weather() -> str:
    try:
        resp = requests.get("https://wttr.in/San+Diego,CA?format=j1", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        curr    = data["current_condition"][0]
        weather = data["weather"][0]
        desc     = curr["weatherDesc"][0]["value"]
        temp_f   = curr["temp_F"]
        feels_f  = curr["FeelsLikeF"]
        humidity = curr["humidity"]
        high_f   = weather["maxtempF"]
        low_f    = weather["mintempF"]
        uv       = weather["uvIndex"]
        return (
            f"{desc}. Currently {temp_f}F (feels like {feels_f}F). "
            f"High {high_f}F / Low {low_f}F. Humidity {humidity}%. UV index {uv}."
        )
    except Exception as e:
        return f"Weather unavailable ({e})"


def get_briefing(weather: str, today: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Today is {today}. I am in San Diego, CA.

Live weather: {weather}

Write my daily Life OS briefing. Use plain text only — no markdown, no asterisks, no bullet symbols. Use ALL CAPS section headers.

WEATHER
Two sentences on today's conditions and what to expect throughout the day.

OUTFIT
Casual look and business/meeting look based on the weather. Be specific about layers, shoes, accessories.

SAN DIEGO TODAY
Three specific things happening or worth doing in San Diego today. Include seasonal events, outdoor activities, local hotspots, or community happenings relevant to this time of year.

NETWORKING
One specific, actionable networking move to make today. Could be a DM, an event, a LinkedIn post, a coffee invite — make it concrete.

Keep total response under 350 words. No fluff."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def send_telegram(token: str, chat_id: str, message: str) -> None:
    try:
        url  = f"https://api.telegram.org/bot{token.strip()}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id.strip(), "text": message}).encode()
        req  = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        print("Telegram sent.")
    except Exception as e:
        print(f"Telegram FAILED: {e}")


if __name__ == "__main__":
    today   = datetime.now().strftime("%A, %B %d, %Y")
    print(f"Life OS — {today}\n")

    weather = get_weather()
    print(f"Weather fetched: {weather}\n")

    briefing = get_briefing(weather, today)
    print(briefing)

    token    = os.getenv("TELEGRAM_TOKEN", "")
    chat_id  = os.getenv("TELEGRAM_CHAT_ID", "")

    if token and chat_id:
        header  = f"Life OS — {today}\n{'─' * 28}\n\n"
        send_telegram(token, chat_id, header + briefing)
    else:
        print("\nTelegram not configured — skipping.")
