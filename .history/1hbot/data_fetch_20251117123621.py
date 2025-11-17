# data_fetch.py
import pandas as pd
from bitget_api import bitget_public_get


def fetch_1h_candles(cfg, limit=300):
    """
    Bitget Futures (UMCBL) 1h Candle を取得
    正しい V2 API を使用
    """
    symbol = cfg["trade"]["symbol"]

    # 正しいエンドポイント（これ以外全部エラー）
    url = "/api/mix/v2/market/candles"

    params = {
        "symbol": symbol,
        "granularity": 3600,
        "limit": limit
    }

    # 呼び出し（bitget_public_get は base_url を内部で付ける）
    j = bitget_public_get(cfg, url, params)

    # V2 は list-of-list で返すため、そのまま DataFrame 化
    if not isinstance(j, list) or len(j) == 0:
        raise Exception(f"Invalid candle data: {j}")

    df = pd.DataFrame(
        j,
        columns=["ts", "open", "high", "low", "close", "volume"]
    )

    # 型変換
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # 古い→新しい順に揃える
    df = df.sort_values("ts").reset_index(drop=True)

    return df
