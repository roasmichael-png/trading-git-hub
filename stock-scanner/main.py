from datetime import date
from scanner.client import get_client
from scanner.scan import run_scan
from scanner.telegram import send_telegram
import config


def print_account():
    client = get_client()
    account = client.get_account()
    print(f"Account status : {account.status}")
    print(f"Equity         : ${float(account.equity):,.2f}")
    print(f"Cash           : ${float(account.cash):,.2f}")
    print(f"Buying power   : ${float(account.buying_power):,.2f}\n")


def build_message(hits: list[dict]) -> str:
    today = date.today().strftime("%b %d")
    if not hits:
        return f"📊 *QQQ Scanner — {today}*\n\nNo setups found today."

    lines = [f"📊 *QQQ Scanner — {today}*", f"_{len(hits)} setup(s) found_\n"]
    for h in hits:
        lines.append(
            f"*{h['symbol']}* ${h['close']:.2f}\n"
            f"  StochRSI K={h['srsi_k']} D={h['srsi_d']}\n"
            f"  MACD={h['macd']:.2f} Signal={h['macd_signal']:.2f}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print_account()
    hits = run_scan()

    if not hits:
        print("No setups found today.")
    else:
        print(f"\n{'='*50}")
        print(f"  {len(hits)} SETUP(S) FOUND")
        print(f"{'='*50}")
        print(f"{'SYM':<6} {'CLOSE':>8} {'K':>6} {'D':>6} {'MACD':>8} {'SIG':>8}")
        print(f"{'-'*50}")
        for h in hits:
            print(
                f"{h['symbol']:<6} {h['close']:>8.2f} "
                f"{h['srsi_k']:>6.1f} {h['srsi_d']:>6.1f} "
                f"{h['macd']:>8.2f} {h['macd_signal']:>8.2f}"
            )

    # Telegram disabled until credentials confirmed working
    # if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
    #     msg = build_message(hits)
    #     send_telegram(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, msg)
    #     print("\nTelegram notification sent.")
