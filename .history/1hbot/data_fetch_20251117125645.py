# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get


def fetch_1h_candles(cfg, limit=300):
    """
    Bitget Futures (UMCBL) 1h Candle を取得
    正しい API: /api/mix/v1/market/candles
    """

    symbol = cfg["trade"]["symbol"]  # BTCUSDT_UMCBL

    path = "/api/mix/v1/market/candles"

    params = {
        "symbol": symbol,
        "granularity": 3600,  # 1 hour
        "limit": limit        # 300 本
    }

    # GET リクエスト
    j = bitget_public_get(cfg, path, params)

    # futures はリスト形式で返る
    # [ [timestamp, open, high, low, close, volume], ... ]
    if not isinstance(j, list) or len(j) == 0:
        raise Exception(f"Invalid candle data: {j}")

    df = pd.DataFrame(
        j,
        columns=["ts", "open", "high", "low", "close", "volume"]
    )

    # timestamp → datetime
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")

    # 数値変換
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # 古い→新しい順
    df = df.sort_values("ts").reset_index(drop=True)

    return df


def compute_indicators(df, params):
    ma_period = params["ma_period"]
    range_lb = params["range_lb"]

    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / \
                      (df["range_high"] - df["range_low"])

    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)
