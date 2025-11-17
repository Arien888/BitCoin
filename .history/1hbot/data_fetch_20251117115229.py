# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get

def fetch_1h_candles(cfg, limit=300):
    """
    Bitget Futures(UMCBL) の 1時間足を取得する。
    public API なので sign は不要。
    """
    symbol = cfg["trade"]["symbol"]

    j = bitget_public_get(
        "/api/mix/v1/market/history-candles",
        {
            "symbol": symbol,
            "granularity": 3600,  # 1h
            "size": limit         # futures は limit ではなく size
        }
    )

    data = j.get("data", [])
    if not data:
        raise Exception(f"No candle data: {j}")

    # data: [[ts, open, high, low, close, volume, quoteVolume], ...]
    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
    )

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df
