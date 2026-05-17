import json
import os
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


def score(h: dict) -> int:
    s = 0
    k = h["srsi_k"]
    if k < 10:   s += 5
    elif k < 15: s += 4
    elif k < 20: s += 3
    elif k < 25: s += 2
    elif k < 30: s += 1
    if h["macd"] > h["macd_signal"]: s += 3   # already crossed up
    rvol = h.get("rvol", 0)
    if rvol >= 2.0:   s += 3
    elif rvol >= 1.5: s += 2
    elif rvol >= 1.2: s += 1
    return s


def format_hit(h: dict) -> str:
    k    = h["srsi_k"]
    rvol = h.get("rvol", 0)
    macd = h["macd"]
    sig  = h["macd_signal"]
    close = h["close"]

    if k < 10:   strength = "Extremely oversold"
    elif k < 20: strength = "Deeply oversold"
    else:         strength = "Oversold"

    momentum = "MACD crossed up" if macd > sig else "MACD turning up"
    vol_note = f" | Vol {rvol:.1f}x" if rvol >= 1.2 else ""

    entry  = close
    stop   = round(close * 0.93, 2)
    target = round(close * 1.18, 2)

    sc = score(h)
    if sc >= 8:   rating = "STRONG BUY"
    elif sc >= 5: rating = "BUY"
    else:          rating = "WATCH"

    return (
        f"{h['symbol']} [{rating}]\n"
        f"  {strength}, {momentum}{vol_note}\n"
        f"  Entry ~${entry:.2f} | Stop ${stop:.2f} | Target ${target:.2f}"
    )


def build_message(hits: list[dict]) -> str:
    today = date.today().strftime("%b %d")
    if not hits:
        return f"Scanner 1 (Tight Reversal) - {today}\n\nNo setups found."
    ranked = sorted(hits, key=score, reverse=True)
    lines  = [f"Scanner 1 (Tight Reversal) - {today}", f"{len(ranked)} setup(s)\n"]

    # Group by sector
    by_sector: dict[str, list] = {}
    for h in ranked:
        by_sector.setdefault(h.get("sector", "📊 Other"), []).append(h)

    for sector, group in by_sector.items():
        lines.append(f"\n{sector}")
        for h in group:
            lines.append(format_hit(h))
    return "\n".join(lines)


if __name__ == "__main__":
    print_account()
    hits = run_scan()

    if not hits:
        print("No setups found today.")
    else:
        print(f"\n{'='*50}")
        print(f"  SCANNER 1 — {len(hits)} SETUP(S) FOUND")
        print(f"{'='*50}")
        print(f"{'SYM':<6} {'CLOSE':>8} {'K':>6} {'D':>6} {'MACD':>8} {'SIG':>8}")
        print(f"{'-'*50}")
        for h in hits:
            print(
                f"{h['symbol']:<6} {h['close']:>8.2f} "
                f"{h['srsi_k']:>6.1f} {h['srsi_d']:>6.1f} "
                f"{h['macd']:>8.2f} {h['macd_signal']:>8.2f}"
            )

    if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
        send_telegram(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, build_message(hits))

    # Save results for dashboard
    ranked = sorted(hits, key=score, reverse=True)
    results = []
    for h in ranked:
        sc = score(h)
        results.append({
            "symbol":  h["symbol"],
            "sector":  h.get("sector", "📊 Other"),
            "close":   h["close"],
            "rating":  "STRONG BUY" if sc >= 8 else "BUY" if sc >= 5 else "WATCH",
            "note":    format_hit(h).split("\n")[1].strip(),
            "entry":   h["close"],
            "stop":    round(h["close"] * 0.93, 2),
            "target":  round(h["close"] * 1.18, 2),
            "scanner": 1,
        })
    results_path = os.path.join(os.path.dirname(__file__), "..", "results", "scanner_results.json")
    try:
        existing = json.loads(open(results_path).read()) if os.path.exists(results_path) else {}
    except Exception:
        existing = {}
    existing["scanner1"] = results
    existing["timestamp"] = date.today().isoformat()
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(existing, f, indent=2)
