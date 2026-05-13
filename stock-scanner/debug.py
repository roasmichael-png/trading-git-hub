"""Print current indicator values for all QQQ holdings so we can see what's close."""
from scanner.data import fetch_daily_bars
from scanner.indicators import add_indicators
from scanner.scan import QQQ_HOLDINGS

bars = fetch_daily_bars(QQQ_HOLDINGS)

print(f"\n{'SYM':<6} {'CLOSE':>8} {'SRSI_K':>8} {'SRSI_D':>8} {'MACD':>10} {'SIGNAL':>10} {'HIST':>10} {'HIST-1':>10}")
print("-" * 80)

rows = []
for sym, df in bars.items():
    try:
        df = add_indicators(df)
        df = df.dropna(subset=["srsi_k", "srsi_d", "macd", "macd_signal"])
        if len(df) < 3:
            continue
        last  = df.iloc[-1]
        prev  = df.iloc[-2]
        hist_last = last["macd"] - last["macd_signal"]
        hist_prev = prev["macd"] - prev["macd_signal"]
        rows.append((sym, last["close"], last["srsi_k"], last["srsi_d"],
                     last["macd"], last["macd_signal"], hist_last, hist_prev))
    except Exception as e:
        print(f"{sym}: error — {e}")

# sort by stoch RSI K ascending so lowest (most oversold) are at top
rows.sort(key=lambda x: x[2])

for sym, close, k, d, macd, signal, hist, hist_prev in rows:
    print(f"{sym:<6} {close:>8.2f} {k:>8.1f} {d:>8.1f} {macd:>10.2f} {signal:>10.2f} {hist:>10.2f} {hist_prev:>10.2f}")
