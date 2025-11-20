import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://api.bitget.com/api/mix/v1/market/history-candles"


def fetch_batch(symbol="BTCUSDT_UMCBL", granularity=3600, limit=200, end_time=None):
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "limit": limit
    }
    if end_time:
        params["endTime"] = end_time

    r = requests.get(BASE_URL, params=params)

    if r.status_code != 200:
        print("HTTP Error:", r.status_code, r.text)
        return []

    j = r.json()

    data = None

    # dict形式 { "data": [...] }
    if isinstance(j, dict) and "data" in j:
        data = j["data"]

    # list形式 [...]
    elif isinstance(j, list):
        data = j

    if data is None:
        print("Unexpected JSON:", j)
        return []

    # ★ 必ず昇順ソート（古い→新しい）
    data = sorted(data, key=lambda x: int(x[0]))

    return data


def fetch_history_months(months=12):
    print(f"Fetching {months} months of BTCUSDT_UMCBL 1H candles...")

    all_rows = []

    now = datetime.now(timezone.utc)
    target_start = now - timedelta(days=months * 30)
    target_ms = int(target_start.timestamp() * 1000)

    end_time = int(now.timestamp() * 1000)

    while True:

        batch = fetch_batch(end_time=end_time)

        if not batch:
            print("\nNo more data returned. Stopping.")
            break

        all_rows.extend(batch)

        # 最後のローソク足
        last_ts = int(batch[0][0])  # ★ batchは昇順なので最も古いのは index=0

        print(f"Fetched rows: {len(all_rows)}", end="\r")

        # ★ 次のリクエストはさらにさかのぼる（ダブル取得防止）
        end_time = last_ts - 1

        if last_ts < target_ms:
            break

        time.sleep(0.15)

    print(f"\nTotal fetched rows: {len(all_rows)}")

    # DF化
    df = pd.DataFrame(all_rows, columns=[
        "ts", "open", "high", "low", "close", "volume", "quoteVolume"
    ])

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # ソート & 重複削除
    df = df.sort_values("ts").drop_duplicates(subset="ts").reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = fetch_history_months(months=18)
    df.to_csv("btc_1h_full.csv", index=False)
    print("Saved -> btc_1h_full.csv")
