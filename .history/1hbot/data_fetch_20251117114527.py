# data_fetch.py
import pandas as pd

from bitget_api import bitget_public_get


def fetch_1h_candles(cfg: dict, limit: int = 300) -> pd.DataFrame:
    """
    BTCUSDT_UMCBL の1時間足を取得
    """
    symbol = cfg["trade"]["symbol"]  # 例: "BTCUSDT_UMCBL"

    j = bitget_public_get(
        cfg,
        "/api/mix/v1/market/history-candles",
        params={
            "symbol": symbol,
            "granularity": 3600,
            "limit": limit,
        },
    )

    data = j.get("data", [])
    if not data:
        raise Exception(f"No candle data: {j}")

    first = data[0]

    # 形式: [[ts, open, high, low, close, volume, quoteVolume], ...] 前提
    if isinstance(first, list):
        if len(first) == 7:
            cols = ["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
        elif len(first) == 6:
            cols = ["ts", "open", "high", "low", "close", "volume"]
        else:
            raise Exception(f"Unsupported candle format: {first}")

        df = pd.DataFrame(data, columns=cols)

        try:
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        except Exception:
            df["ts"] = pd.to_datetime(df["ts"])

    else:
        # 念のため dict形式にも対応
        df = pd.DataFrame(data)
        ts_col = "ts" if "ts" in df.columns else "timestamp"
        try:
            df["ts"] = pd.to_datetime(df[ts_col], unit="ms")
        except Exception:
            df["ts"] = pd.to_datetime(df[ts_col])

    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df
