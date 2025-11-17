# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get

def fetch_1h_candles(cfg, limit=300):
    """
    Bitget Futures (UMCBL) 1h Candle 正しい API
    """
    symbol = cfg["trade"]["symbol"]   # BTCUSDT_UMCBL

    path = "/api/mix/v1/market/history-candles"

    params = {
        "symbol": symbol,
        "granularity": 3600,   # ← 1h
        "limit": limit
    }

    data = bitget_public_get(cfg, path, params)

    # futures は list-of-list 形式
    # [ [ts, open, high, low, close, volume], ... ]
    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume"]
    )

    # ts はミリ秒
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df
