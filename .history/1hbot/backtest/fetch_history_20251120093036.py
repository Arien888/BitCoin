import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://api.bitget.com/api/mix/v1/market/history-candles"

def fetch_batch(symbol="BTCUSDT_UMCBL", granularity=3600, limit=1000, end_time=None):
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "limit": limit,
    }
    if end_time:
        params["endTime"] = end_time

    r = requests.get(BASE_URL, params=params)

    if r.status_code != 200:
        print("HTTP Error:", r.status_code, r.text)
        return []

    j = r.json()

    # 形式 {"data": [...]} が基本
    if isinstance(j, dict) and "data" in j:
        return j["data"]

    # 稀にリストで来る場合
    if isinstance(j, list):
        return j

    print("Unexpected JSON:", j)
    return []


def fetch_history_months(months=12):
    print(f"Fetching {months} months of BTC 1H candles...")

    all_rows = []

    # ====== 正確に months 以前の日時を計算 ======
    now = datetime.now(timezone.utc)
    target_start = now - timedelta(days=months * 30)
    target_ms = int(target_start.timestamp() * 1000)

    # 初回 end_time は現在時刻（最新から遡る）
    end_time = int(now.timestamp() * 1000)

    # ====== 過去方向に取得 ======
    while True:

        batch = fetch_batch(end_time=end_time)

        if not batch:
            print("\nNo more data returned. Stopping.")
            break

        # 重複排除しながら追加
        all_rows.extend(batch)

        # 最後の timestamp
        last_ts = batch[-1][0]
        end_time = int(last_ts)

        print(f"Fetched rows: {len(all_rows)}", end="\r")

        # 目的の始点（target_start）まで遡ったら停止
        if last_ts < target_ms:
            break

        # API 負荷対策
        time.sleep(0.15)

    print(f"\nTotal fetched rows: {len(all_rows)}")

    # ====== DF化 ======
    df = pd.DataFrame(all_rows, columns=[
        "ts", "open", "high", "low", "close", "volume", "quoteVolume"
    ])

    # 数値変換
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)

    # 古い順にソート
    df = df.sort_values("ts").reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = fetch_history_months(months=18)
    df.to_csv("btc_1h_full.csv", index=False)
    print("Saved -> btc_1h_full.csv")
