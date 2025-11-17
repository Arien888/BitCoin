# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get

def fetch_1h_candles(cfg, limit=300):
    symbol = cfg["trade"]["symbol"]  # BTCUSDT
    path = "/api/v2/mix/market/history-candles"

    # 1Hローソク足 × limit 分過去を要求
    end_ts = int(time.time() * 1000)
    start_ts = end_ts - limit * 3600 * 1000

    params = {
        "symbol": symbol,
        "granularity": "1H",
        "productType": "usdt-futures",
        "startTime": start_ts,
        "endTime": end_ts
    }

    data = bitget_public_get(cfg, path, params)

    if not isinstance(data, list) or len(data) == 0:
        raise Exception(f"Invalid candle data: {data}")

    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume"]
    )

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df.sort_values("ts").reset_index(drop=True)


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
