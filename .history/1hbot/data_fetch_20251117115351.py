# data_fetch.py
import time
import pandas as pd
from bitget_api import bitget_public_get


def fetch_1h_candles(cfg, limit=300):
    """
    Bitget UMCBL 1h 足（history-candles）
    V1/V2 のレスポンス揺れに完全対応
    """
    symbol = cfg["trade"]["symbol"]

    # 時間（ms）
    end = int(time.time() * 1000)
    start = end - limit * 3600 * 1000

    j = bitget_public_get(
        "/api/mix/v1/market/history-candles",
        {
            "symbol": symbol,
            "granularity": 3600,
            "startTime": start,
            "endTime": end
        }
    )

    # ---- ① j が list の場合 ----
    if isinstance(j, list):
        data = j

    # ---- ② j が dict で data フィールドがある場合 ----
    elif isinstance(j, dict):
        data = j.get("data", [])
    else:
        raise Exception(f"Unexpected candle response: {j}")

    if not data:
        raise Exception(f"No candle data: {j}")

    # ---- dataframe 変換 ----
    # data 形式例:
    # [ts, open, high, low, close, volume, quoteVolume]
    first = data[0]
    if len(first) == 7:
        df = pd.DataFrame(
            data,
            columns=["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
        )
    elif len(first) == 6:
        df = pd.DataFrame(
            data,
            columns=["ts", "open", "high", "low", "close", "volume"]
        )
        df["quoteVolume"] = 0
    else:
        raise Exception(f"Unknown candle format: {first}")

    # ---- 型変換 ----
    try:
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    except:
        df["ts"] = pd.to_datetime(df["ts"])

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df
