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


def check_signals(df: pd.DataFrame) -> bool:
    df = df.dropna(subset=["srsi_k", "srsi_d", "macd", "macd_signal"])
    if len(df) < 4:
        return False

    last  = df.iloc[-1]
    prev  = df.iloc[-2]
    prev2 = df.iloc[-3]

    # stoch RSI: K below 20 and K above D (oversold with bullish momentum)
    srsi_oversold = last["srsi_k"] < 20
    srsi_bullish = last["srsi_k"] > last["srsi_d"]

    # MACD: below zero AND below signal, histogram shrinking fast (>15% over 2 bars)
    macd_below_zero = last["macd"] < 0
    macd_below_signal = last["macd"] < last["macd_signal"]
    hist_last  = last["macd"] - last["macd_signal"]
    hist_prev  = prev["macd"] - prev["macd_signal"]
    hist_prev2 = prev2["macd"] - prev2["macd_signal"]
    improving = hist_last > hist_prev > hist_prev2
    convergence_rate = (hist_last - hist_prev2) / abs(hist_prev2) if hist_prev2 != 0 else 0
    # gap must be closing fast AND be small relative to price (filters bad data / far-from-cross)
    gap_pct_of_price = abs(hist_last) / last["close"]
    macd_converging = improving and convergence_rate >= 0.15 and gap_pct_of_price < 0.05

    return srsi_oversold and srsi_bullish and macd_below_zero and macd_below_signal and macd_converging
