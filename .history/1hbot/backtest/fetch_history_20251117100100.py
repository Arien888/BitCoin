import requests
import pandas as pd
import time
from datetime import datetime

BASE_URL = "https://api.bitget.com/api/spot/v1/market/history-candles"

def fetch_batch(symbol="BTCUSDT_SPBL", period="1h", limit=200, after=None):
    """
    Bitgetの歴史1h足データを1バッチ取得（最大200本）
    after には Unix ミリ秒を指定すると、その時間より「前のデータ」が取得される。
    """
    params = {
        "symbol": symbol,
        "period": period,
        "limit": limit
    }
    if after is not None:
        params["after"] = after

    r = requests.get(BASE_URL, params=params)
    if r.status_code != 200:
        print("Error:", r.text)
        return None

    data = r.json().get("data", [])
    return data

def fetch_history_months(months=6):
    """
    過去 n か月分の1h足をすべて取得し、DataFrameで返す。
    """
    all_data = []
    now_ms = int(time.time() * 1000)  # 現在時刻（ms）
    after = now_ms

    print(f"Fetching ~{months} months of 1h data...")

    # 1ヶ月 ≒ 30 days = 30 * 24 = 720本
    # 6ヶ月だと 4320本程度
    target_count = months * 720

    while len(all_data) < target_count:
        batch = fetch_batch(after=after)

        if not batch:
            print("No more data. Ending.")
            break

        all_data.extend(batch)

        # API負荷軽減
        time.sleep(0.2)

        # 最後のローソク足の timestamp（ms）を次の after に使う
        last_ts = batch[-1]["ts"]
        after = int(last_ts)

        print(f"Fetched: {len(all_data)} rows", end="\r")

    print(f"\nTotal fetched rows: {len(all_data)}")

    # DataFrameに変換
    df = pd.DataFrame(all_data, columns=[
        "ts", "open", "high", "low", "close", "quoteVol", "baseVol", "usdVol"
    ])

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("ts").reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = fetch_history_months(months=6)
    df.to_csv("btc_1h_full.csv", index=False)
    print("Saved -> btc_1h_full.csv")
