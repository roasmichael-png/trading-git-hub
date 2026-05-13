import config
import urllib.request
import urllib.parse

token = config.TELEGRAM_TOKEN.strip()
chat_id = config.TELEGRAM_CHAT_ID.strip()

print(f"Token length : {len(token)}")
print(f"Token start  : {token[:10]}...")
print(f"Chat ID      : '{chat_id}'")

url = f"https://api.telegram.org/bot{token}/getMe"
try:
    resp = urllib.request.urlopen(url, timeout=10)
    print(f"Bot valid    : YES — {resp.read().decode()[:80]}")
except Exception as e:
    print(f"Bot error    : {e}")
