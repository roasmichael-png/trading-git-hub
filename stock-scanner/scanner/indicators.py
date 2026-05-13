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

    # MACD: still below signal but histogram shrinking for 2+ bars (converging)
    macd_below_signal = last["macd"] < last["macd_signal"]
    hist_last  = last["macd"] - last["macd_signal"]
    hist_prev  = prev["macd"] - prev["macd_signal"]
    hist_prev2 = prev2["macd"] - prev2["macd_signal"]
    macd_converging = hist_last > hist_prev > hist_prev2

    return srsi_oversold and srsi_bullish and macd_below_signal and macd_converging
