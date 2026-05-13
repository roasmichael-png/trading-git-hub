import urllib.request
import urllib.parse


def send_telegram(token: str, chat_id: str, message: str) -> None:
    token = token.strip()
    chat_id = chat_id.strip()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
    }).encode()
    req = urllib.request.Request(url, data=data)
    urllib.request.urlopen(req, timeout=10)
