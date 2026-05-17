"""Scanner 2 — Loose Reversal. Wider thresholds than Scanner 1."""
from datetime import date
from scanner.client import get_client
from scanner.data import fetch_daily_bars
from scanner.indicators2 import add_indicators, check_signals_loose
from scanner.scan import _all_stocks, TOP_ETFS, get_sector
from scanner.telegram import send_telegram
import config
import json
import os
import time


def print_account():
    client = get_client()
    account = client.get_account()
    print(f"Account status : {account.status}")
    print(f"Equity         : ${float(account.equity):,.2f}\n")


def _score(h):
    s = 0
    k = h["srsi_k"]
    if k < 15:   s += 4
    elif k < 20: s += 3
    elif k < 25: s += 2
    elif k < 30: s += 1
    if h["macd"] > h["macd_signal"]: s += 3
    rvol = h.get("rvol", 0)
    if rvol >= 2.0:   s += 3
    elif rvol >= 1.5: s += 2
    elif rvol >= 1.2: s += 1
    return s


def run_loose_scan() -> list[dict]:
    stocks = list(dict.fromkeys(_all_stocks() + TOP_ETFS))
    print(f"[Scanner 2] Scanning {len(stocks)} stocks/ETFs...")

    hits = []
    for i in range(0, len(stocks), 50):
        batch = stocks[i:i + 50]
        try:
            bars = fetch_daily_bars(batch)
        except Exception:
            time.sleep(2)
            continue
        for sym, df in bars.items():
            try:
                df = add_indicators(df)
                if check_signals_loose(df):
                    last = df.iloc[-1]
                    hits.append({
                        "symbol":      sym,
                        "sector":      get_sector(sym),
                        "close":       round(last["close"], 2),
                        "srsi_k":      round(last["srsi_k"], 1),
                        "srsi_d":      round(last["srsi_d"], 1),
                        "macd":        round(last["macd"], 2),
                        "macd_signal": round(last["macd_signal"], 2),
                        "rvol":        round(last["rvol"], 2) if "rvol" in last and last["rvol"] == last["rvol"] else 0.0,
                    })
            except Exception:
                continue
        time.sleep(0.3)
    return hits


if __name__ == "__main__":
    print_account()
    hits = run_loose_scan()

    if not hits:
        print("No setups found today.")
    else:
        print(f"\n{'='*50}\n  SCANNER 2 — {len(hits)} SETUP(S)\n{'='*50}")
        for h in hits:
            print(f"{h['symbol']:<8} {h['close']:>8.2f}  K={h['srsi_k']}  {h['sector']}")

    if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
        today = date.today().strftime("%b %d")
        if not hits:
            msg = f"Scanner 2 (Loose Reversal) - {today}\n\nNo setups found."
        else:
            ranked = sorted(hits, key=_score, reverse=True)
            lines = [f"Scanner 2 (Loose Reversal) - {today}", f"{len(ranked)} setup(s)\n"]

            by_sector: dict[str, list] = {}
            for h in ranked:
                by_sector.setdefault(h.get("sector", "📊 Other"), []).append(h)

            for sector, group in by_sector.items():
                lines.append(f"\n{sector}")
                for h in group:
                    k     = h["srsi_k"]
                    macd  = h["macd"]
                    sig   = h["macd_signal"]
                    rvol  = h.get("rvol", 0)
                    close = h["close"]
                    strength = "Deeply oversold" if k < 20 else "Oversold"
                    momentum = "MACD crossed up" if macd > sig else "MACD turning up"
                    vol_note = f" | Vol {rvol:.1f}x" if rvol >= 1.2 else ""
                    stop   = round(close * 0.93, 2)
                    target = round(close * 1.18, 2)
                    sc = _score(h)
                    rating = "STRONG BUY" if sc >= 7 else "BUY" if sc >= 4 else "WATCH"
                    lines.append(
                        f"{h['symbol']} [{rating}]\n"
                        f"  {strength}, {momentum}{vol_note}\n"
                        f"  Entry ~${close:.2f} | Stop ${stop:.2f} | Target ${target:.2f}"
                    )
            msg = "\n".join(lines)
        send_telegram(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, msg)

    # Save results for dashboard
    ranked = sorted(hits, key=_score, reverse=True)
    s2_results = []
    for h in ranked:
        sc = _score(h)
        close = h["close"]
        s2_results.append({
            "symbol":  h["symbol"],
            "sector":  h.get("sector", "📊 Other"),
            "close":   close,
            "rating":  "STRONG BUY" if sc >= 7 else "BUY" if sc >= 4 else "WATCH",
            "note":    f"Loose reversal | StochRSI {h['srsi_k']} | MACD {'up' if h['macd'] > h['macd_signal'] else 'turning'}",
            "entry":   close,
            "stop":    round(close * 0.93, 2),
            "target":  round(close * 1.18, 2),
            "scanner": 2,
        })
    results_path = os.path.join(os.path.dirname(__file__), "..", "results", "scanner_results.json")
    try:
        existing = json.loads(open(results_path).read()) if os.path.exists(results_path) else {}
    except Exception:
        existing = {}
    existing["scanner2"] = s2_results
    existing["timestamp"] = date.today().isoformat()
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(existing, f, indent=2)
