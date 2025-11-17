# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get

# data_fetch.py の一部
def fetch_1h_candles(cfg, limit=300):
    symbol = cfg["trade"]["symbol"]  # ex: "BTCUSDT_UMCBL"
    path = "/api/v2/mix/market/history-candles"  # または /api/v2/mix/market/candles

    params = {
        "symbol": symbol,
        "granularity": "1H",             # ドキュメント通り文字列形式
        "limit": limit,
        "productType": "usdt-futures"    # Futures 用パラメータ
    }

    data = bitget_public_get(cfg, path, params)
    # …その後、DataFrame 化など…


    if not isinstance(data, list) or len(data) == 0:
        raise Exception(f"Invalid candle data: {data}")

    df = pd.DataFrame(
        data,
        columns=["ts", "open", "high", "low", "close", "volume"]
    )

    try:
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    except:
        df["ts"] = pd.to_datetime(df["ts"])

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df


def compute_indicators(df, params):
    """
    MA + Range + Prev をまとめて計算する
    live_bot 用のインジケータ統合関数
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

    # Prev
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)
