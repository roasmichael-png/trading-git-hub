"""Scanner 3 — Trend Pullback System."""
import time
from datetime import date
from scanner.client import get_client
from scanner.data import fetch_daily_bars, fetch_crypto_bars
from scanner.indicators_trend import add_indicators, add_weekly, check_trend_signals
from scanner.scan import _all_stocks, TOP_ETFS, CRYPTOS
from scanner.telegram import send_telegram
import config


MARKET_SYMBOLS = ["QQQ", "SPY"]


def print_account():
    client = get_client()
    account = client.get_account()
    print(f"Account  : {account.status}")
    print(f"Equity   : ${float(account.equity):,.2f}\n")


def get_market_data() -> dict:
    """Fetch QQQ and SPY once for market filter and relative strength."""
    bars = fetch_daily_bars(MARKET_SYMBOLS)
    result = {}
    for sym in MARKET_SYMBOLS:
        if sym in bars:
            df = add_indicators(bars[sym])
            result[sym] = df
    return result


def check_market_conditions(market: dict) -> tuple[bool, str]:
    """Returns (is_ok, reason_if_not)."""
    qqq = market.get("QQQ")
    spy = market.get("SPY")

    if qqq is None or spy is None:
        return True, ""  # can't check, allow through

    qqq_last = qqq.iloc[-1]
    spy_last = spy.iloc[-1]

    if qqq_last["close"] < qqq_last["ema21"]:
        return False, "QQQ below 21 EMA"
    if spy_last["close"] < spy_last["sma50"]:
        return False, "SPY below 50 SMA"

    return True, ""


def run_trend_scan() -> list[dict]:
    print("Fetching market data...")
    market = get_market_data()
    qqq_df = market.get("QQQ")

    market_ok, reason = check_market_conditions(market)
    if not market_ok:
        print(f"⚠️  Market conditions weak: {reason} — only A+ setups shown")

    stocks = list(dict.fromkeys(_all_stocks() + [s for s in TOP_ETFS if s not in ("TLT", "HYG", "AGG", "BND")]))
    cryptos = CRYPTOS

    print(f"[Scanner 3] Scanning {len(stocks)} stocks/ETFs + {len(cryptos)} cryptos...")

    hits = []
    for sym_list, fetch_fn, use_qqq in [
        (stocks, fetch_daily_bars, qqq_df),
        (cryptos, fetch_crypto_bars, None),  # no QQQ RS for crypto
    ]:
        for i in range(0, len(sym_list), 50):
            batch = sym_list[i:i + 50]
            try:
                bars = fetch_fn(batch)
            except Exception:
                time.sleep(2)
                continue

            for sym, df in bars.items():
                if sym in ("QQQ", "SPY"):
                    continue
                try:
                    df = add_indicators(df)
                    df = add_weekly(df)
                    if check_trend_signals(df, use_qqq):
                        last = df.iloc[-1]
                        hits.append({
                            "symbol":   sym,
                            "close":    round(last["close"], 2),
                            "ema21":    round(last["ema21"], 2),
                            "sma50":    round(last["sma50"], 2),
                            "rsi":      round(last["rsi"], 1),
                            "srsi_k":   round(last["srsi_k"], 1),
                            "macd":     round(last["macd"], 2),
                            "macd_sig": round(last["macd_signal"], 2),
                            "rvol":     round(last["rvol"], 2),
                        })
                except Exception:
                    continue
            time.sleep(0.3)

    return hits


if __name__ == "__main__":
    print_account()
    hits = run_trend_scan()

    if not hits:
        print("No trend setups found today.")
    else:
        print(f"\n{'='*70}")
        print(f"  SCANNER 3 (TREND PULLBACK) — {len(hits)} SETUP(S)")
        print(f"{'='*70}")
        print(f"{'SYM':<8} {'CLOSE':>8} {'EMA21':>8} {'SMA50':>8} {'RSI':>6} {'K':>6} {'MACD':>8} {'RVOL':>6}")
        print(f"{'-'*70}")
        for h in hits:
            print(
                f"{h['symbol']:<8} {h['close']:>8.2f} {h['ema21']:>8.2f} "
                f"{h['sma50']:>8.2f} {h['rsi']:>6.1f} {h['srsi_k']:>6.1f} "
                f"{h['macd']:>8.2f} {h['rvol']:>6.2f}x"
            )

    if config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID:
        today = date.today().strftime("%b %d")
        if not hits:
            msg = f"Scanner 3 (Trend Pullback) - {today}\n\nNo setups found."
        else:
            def _score(h):
                s = 0
                k = h["srsi_k"]
                if k < 15:   s += 5
                elif k < 20: s += 4
                elif k < 25: s += 3
                elif k < 30: s += 2
                rvol = h["rvol"]
                if rvol >= 2.5:   s += 4
                elif rvol >= 2.0: s += 3
                elif rvol >= 1.5: s += 2
                elif rvol >= 1.2: s += 1
                if h["rsi"] < 40: s += 2
                elif h["rsi"] < 50: s += 1
                if h["macd"] > h["macd_sig"]: s += 2
                return s

            ranked = sorted(hits, key=_score, reverse=True)
            lines  = [f"Scanner 3 (Trend Pullback) - {today}", f"{len(ranked)} setup(s)\n"]
            for h in ranked:
                k     = h["srsi_k"]
                rvol  = h["rvol"]
                rsi   = h["rsi"]
                close = h["close"]
                ema21 = h["ema21"]

                if k < 20:        pullback = "Deeply oversold pullback"
                elif rsi < 45:    pullback = "Clean RSI reset"
                else:              pullback = "Controlled pullback"

                vol = "Heavy volume" if rvol >= 2.0 else "Above-avg volume" if rvol >= 1.5 else "Normal volume"
                near = "at EMA21" if abs(close - ema21) / ema21 < 0.01 else "near EMA21"

                stop   = round(close * 0.90, 2)   # 10% trail per strategy rules
                target = round(close * 1.20, 2)   # 20% target

                sc = _score(h)
                rating = "STRONG BUY" if sc >= 9 else "BUY" if sc >= 6 else "WATCH"

                lines.append(
                    f"{h['symbol']} [{rating}]\n"
                    f"  {pullback} {near} | {vol} ({rvol:.1f}x)\n"
                    f"  Entry ~${close:.2f} | Stop ${stop:.2f} | Target ${target:.2f}"
                )
            msg = "\n".join(lines)
        send_telegram(config.TELEGRAM_TOKEN, config.TELEGRAM_CHAT_ID, msg)
