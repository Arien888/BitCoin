import requests
import pandas as pd
import time

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

    # ★ ケース1: {"data": [...]} → dict 形式
    if isinstance(j, dict) and "data" in j:
        return j["data"]

    # ★ ケース2: 直接リストが返ってくる場合
    if isinstance(j, list):
        return j

    print("Unexpected JSON:", j)
    return []


def fetch_history_months(months=6):
    print(f"Fetching ~{months} months of BTCUSDT_UMCBL 1H candles...")

    all_rows = []
    end_time = int(time.time() * 1000)

    target_rows = months * 30 * 24  # 1ヶ月=720本 → 6ヶ月=4320本

    while len(all_rows) < target_rows:
        batch = fetch_batch(end_time=end_time)

        if not batch:
            print("No more data returned. Ending.")
            break

        all_rows.extend(batch)

        # 過去方向へ遡る
        last_ts = batch[-1][0]  # 最後のローソク足の timestamp(ms)
        end_time = int(last_ts)

        print(f"Fetched: {len(all_rows)} rows", end="\r")

        time.sleep(0.15)

    print(f"\nTotal fetched rows: {len(all_rows)}")

    # DF化
    df = pd.DataFrame(all_rows, columns=[
        "ts", "open", "high", "low", "close", "volume", "quoteVolume"
    ])

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df.sort_values("ts").reset_index(drop=True)


if __name__ == "__main__":
    df = fetch_history_months(months=6)
    df.to_csv("btc_1h_full.csv", index=False)
    print("Saved -> btc_1h_full.csv")
