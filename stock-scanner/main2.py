"""Scanner 2 — Loose Reversal. Wider thresholds than Scanner 1."""
from datetime import date
from scanner.client import get_client
from scanner.data import fetch_daily_bars, fetch_crypto_bars
from scanner.indicators2 import add_indicators, check_signals_loose
from scanner.scan import _all_stocks, TOP_ETFS, CRYPTOS
from scanner.telegram import send_telegram
import config
import time


def print_account():
    client = get_client()
    account = client.get_account()
    print(f"Account status : {account.status}")
    print(f"Equity         : ${float(account.equity):,.2f}\n")


def run_loose_scan() -> list[dict]:
    stocks = list(dict.fromkeys(_all_stocks() + TOP_ETFS))
    print(f"[Scanner 2] Scanning {len(stocks)} stocks/ETFs...")

    hits = []
    for sym_list, fetch_fn in [(stocks, fetch_daily_bars)]:
        for i in range(0, len(sym_list), 50):
            batch = sym_list[i:i + 50]
            try:
                bars = fetch_fn(batch)
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
                            "close":       round(last["close"], 2),
                            "srsi_k":      round(last["srsi_k"], 1),
                            "srsi_d":      round(last["srsi_d"], 1),
                            "macd":        round(last["macd"], 2),
                            "macd_signal": round(last["macd_signal"], 2),
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
        print(f"\n{'='*50}")
        print(f"  SCANNER 2 — {len(hits)} SETUP(S) FOUND")
        print(f"{'='*50}")
        print(f"{'SYM':<8} {'CLOSE':>8} {'K':>6} {'D':>6} {'MACD':>8} {'SIG':>8}")
        print(f"{'-'*50}")
        for h in hits:
            print(
                f"{h['symbol']:<8} {h['close']:>8.2f} "
                f"{h['srsi_k']:>6.1f} {h['srsi_d']:>6.1f} "
                f"{h['macd']:>8.2f} {h['macd_signal']:>8.2f}"
            )

    if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
        today = date.today().strftime("%b %d")
        if not hits:
            msg = f"Scanner 2 (Loose Reversal) - {today}\n\nNo setups found."
        else:
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

            ranked = sorted(hits, key=_score, reverse=True)
            lines  = [f"Scanner 2 (Loose Reversal) - {today}", f"{len(ranked)} setup(s)\n"]
            for h in ranked:
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
