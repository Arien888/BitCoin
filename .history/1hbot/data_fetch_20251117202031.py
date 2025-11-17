# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get
import time

def fetch_1h_candles(cfg, limit=200):
    import time
    symbol = cfg["trade"]["symbol"]  # "BTCUSDT"
    path = "/api/v2/mix/market/history-candles"

    params = {
        "symbol": symbol,
        "granularity": "1H",
        "productType": "usdt-futures",
        "limit": limit
    }

    data = bitget_public_get(cfg, path, params)

    if not isinstance(data, list) or len(data) == 0:
        raise Exception(f"Invalid candle data: {data}")

    # Bitget は7列返す → 7列指定
    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
    )

    # 不要列を削除
    df = df.drop(columns=["quoteVolume"])

    # timestamp
    try:
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    except:
        df["ts"] = pd.to_datetime(df["ts"])

    # 数値変換
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df


def compute_indicators(df, params):
    """
    MA + Range + Prev をまとめて計算
    """
    ma_period = params["ma_period"]
    range_lb  = params["range_lb"]

    # MA
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()

    # Range
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"]  = df["low"].rolling(range_lb).min()
    df["range_pos"]  = (df["close"] - df["range_low"]) / (
        df["range_high"] - df["range_low"]
    )

    # Prev close / direction
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)
