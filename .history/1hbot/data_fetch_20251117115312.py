# data_fetch.py
import time
import pandas as pd
from bitget_api import bitget_public_get


def fetch_1h_candles(cfg, limit=300):
    """
    Bitget Futures UMCBL の 1h 足を正しく取得
    history-candles は startTime & endTime 指定が必須
    """
    symbol = cfg["trade"]["symbol"]

    # 現在時刻（ms）
    end = int(time.time() * 1000)
    # 過去300本 → 300時間 → 300 * 3600 * 1000
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

    data = j.get("data", [])
    if not data:
        raise Exception(f"No candle data: {j}")

    # フォーマット： [ts, open, high, low, close, volume, quoteVolume]
    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
    )

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df
