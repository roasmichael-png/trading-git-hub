import urllib.request
import urllib.parse
import traceback


def send_telegram(token: str, chat_id: str, message: str) -> bool:
    try:
        token = token.strip()
        chat_id = chat_id.strip()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id":    chat_id,
            "text":       message,
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        print("Telegram sent.")
        return True
    except Exception as e:
        print(f"Telegram FAILED: {e}")
        traceback.print_exc()
        return False
