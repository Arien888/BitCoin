from bitget_api import bitget_public_get
import pandas as pd

def fetch_1h_candles(cfg, limit=300):
    symbol = cfg["trade"]["symbol"]  # BTCUSDT_UMCBL

    # mix futures → size を使う
    j = bitget_public_get(
        path="/api/mix/v1/market/history-candles",
        params={
            "symbol": symbol,
            "granularity": 3600,  # 1時間足
            "size": limit
        }
    )

    data = j.get("data", [])
    if not data or not isinstance(data, list):
        raise Exception(f"Invalid candle data: {j}")

    # data は [[ts, open, high, low, close, volume, quoteVolume], ...]
    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
    )

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df
