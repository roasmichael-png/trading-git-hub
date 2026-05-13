import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import StochRSIIndicator


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["close"]

    df["sma200"] = SMAIndicator(close, window=200).sma_indicator()

    stochrsi = StochRSIIndicator(close, window=14, smooth1=3, smooth2=3)
    df["srsi_k"] = stochrsi.stochrsi_k() * 100
    df["srsi_d"] = stochrsi.stochrsi_d() * 100

    macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    return df


def check_signals_loose(df: pd.DataFrame) -> bool:
    df = df.dropna(subset=["srsi_k", "srsi_d", "macd", "macd_signal"])
    if len(df) < 4:
        return False

    last  = df.iloc[-1]
    prev  = df.iloc[-2]
    prev2 = df.iloc[-3]

    # stoch RSI: K below 30 and K above D or within 3 points
    srsi_oversold = last["srsi_k"] < 30
    srsi_bullish = last["srsi_k"] >= last["srsi_d"] - 3

    # MACD: below zero AND below signal, histogram converging (loosened thresholds)
    macd_below_zero = last["macd"] < 0
    macd_below_signal = last["macd"] < last["macd_signal"]
    hist_last  = last["macd"] - last["macd_signal"]
    hist_prev  = prev["macd"] - prev["macd_signal"]
    hist_prev2 = prev2["macd"] - prev2["macd_signal"]
    improving = hist_last > hist_prev > hist_prev2
    convergence_rate = (hist_last - hist_prev2) / abs(hist_prev2) if hist_prev2 != 0 else 0
    gap_pct_of_price = abs(hist_last) / last["close"]
    macd_converging = improving and convergence_rate >= 0.05 and gap_pct_of_price < 0.12

    return srsi_oversold and srsi_bullish and macd_below_zero and macd_below_signal and macd_converging
