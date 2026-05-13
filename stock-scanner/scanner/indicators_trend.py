import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.volume import OnBalanceVolumeIndicator


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["close"]
    volume = df["volume"]

    df["sma50"]  = SMAIndicator(close, window=50).sma_indicator()
    df["sma200"] = SMAIndicator(close, window=200).sma_indicator()
    df["ema21"]  = EMAIndicator(close, window=21).ema_indicator()

    df["rsi"] = RSIIndicator(close, window=14).rsi()

    stochrsi = StochRSIIndicator(close, window=14, smooth1=3, smooth2=3)
    df["srsi_k"] = stochrsi.stochrsi_k() * 100
    df["srsi_d"] = stochrsi.stochrsi_d() * 100

    macd = MACD(close, window_slow=26, window_fast=12, window_sign=9)
    df["macd"]        = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"]   = macd.macd_diff()

    df["avg_volume"] = volume.rolling(20).mean()
    df["rvol"]       = volume / df["avg_volume"]

    return df


def add_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Resample daily bars to weekly and add weekly indicators."""
    weekly = df["close"].resample("W").last().dropna()
    weekly_ema20 = EMAIndicator(weekly, window=20).ema_indicator()
    # map weekly values back to daily index
    df["weekly_ema20"] = weekly_ema20.reindex(df.index, method="ffill")
    df["weekly_close"] = weekly.reindex(df.index, method="ffill")
    return df


def check_trend_signals(df: pd.DataFrame, qqq_df: pd.DataFrame) -> bool:
    df = df.dropna(subset=["sma50", "sma200", "ema21", "rsi", "srsi_k", "macd", "macd_hist"])
    if len(df) < 5:
        return False

    last  = df.iloc[-1]
    prev  = df.iloc[-2]
    prev2 = df.iloc[-3]

    # --- TREND FILTER ---
    above_50sma  = last["close"] > last["sma50"]
    golden_cross = last["sma50"] > last["sma200"]
    ema21_above  = last["ema21"] > last["sma50"]

    if not (above_50sma and golden_cross):
        return False

    # --- WEEKLY FILTER ---
    if "weekly_ema20" in df.columns and pd.notna(last["weekly_ema20"]):
        above_weekly_ema = last["close"] > last["weekly_ema20"]
        if not above_weekly_ema:
            return False

    # --- PULLBACK CONDITIONS ---
    rsi_reset    = 35 <= last["rsi"] <= 65
    srsi_ok      = last["srsi_k"] < 35
    near_ema21   = last["close"] <= last["ema21"] * 1.03  # within 3% of 21 EMA

    if not (rsi_reset and srsi_ok and near_ema21):
        return False

    # --- MACD IMPROVING ---
    hist_improving = last["macd_hist"] > prev["macd_hist"] > prev2["macd_hist"]
    if not hist_improving:
        return False

    # --- RELATIVE STRENGTH vs QQQ ---
    if qqq_df is not None and len(qqq_df) >= 10:
        stock_return = last["close"] / df.iloc[-10]["close"] - 1
        qqq_return   = qqq_df.iloc[-1]["close"] / qqq_df.iloc[-10]["close"] - 1
        if stock_return < qqq_return:
            return False

    # --- VOLUME (RVOL) ---
    rvol_ok = last["rvol"] >= 1.2 if pd.notna(last["rvol"]) else False
    if not rvol_ok:
        return False

    return True
