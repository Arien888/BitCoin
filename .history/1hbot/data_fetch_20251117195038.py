# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get

# ==============================
# 1h足取得（Bitget Futures）
# ==============================
def fetch_1h_candles(cfg, limit=300):
    symbol = cfg["trade"]["symbol"]

    path = "/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": 3600,
        "limit": limit
    }

    data = bitget_public_get(cfg, path, params)

    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume"]
    )

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df


# ==============================
# テクニカル指標計算
# ==============================
def compute_indicators(df, params):
    ma_period = params["ma_period"]
    range_lb = params["range_lb"]

    # MA
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()

    # Range
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (
        df["range_high"] - df["range_low"]
    )

    # Prev
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)
