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
    if len(df) < 201:
        return False

    df = df.dropna(subset=["sma200", "srsi_k", "srsi_d", "macd", "macd_signal"])
    if len(df) < 3:
        return False

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # price within 3% below the 200 SMA (about to break above)
    near_200 = last["sma200"] * 0.97 <= last["close"] < last["sma200"]

    # stoch RSI below 20 and K crossing above D
    srsi_oversold = last["srsi_k"] < 20
    srsi_cross = prev["srsi_k"] <= prev["srsi_d"] and last["srsi_k"] > last["srsi_d"]

    # MACD below -100 and crossing above signal
    macd_deep = last["macd"] < -100
    macd_cross = prev["macd"] <= prev["macd_signal"] and last["macd"] > last["macd_signal"]

    return near_200 and srsi_oversold and srsi_cross and macd_deep and macd_cross
