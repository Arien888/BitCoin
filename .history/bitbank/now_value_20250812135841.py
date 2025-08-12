import requests
import pandas as pd
import time
import os
import yaml
from datetime import datetime

# config.yaml の読み込み
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 保存先Excelの絶対パス
excel_path = os.path.abspath(os.path.join(BASE_DIR, "..", config["paths"]["asset_excel"]))

# 取得対象ペア
symbols = config.get("symbols", ["btc_jpy"])
# 取得間隔
interval = config.get("interval_seconds", 10)

while True:
    all_data = []
    now = datetime.now()

    for symbol in symbols:
        url = f"https://public.bitbank.cc/{symbol}/ticker"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"HTTPエラー: {symbol}")
            continue

        data = res.json()
        if data.get("success") != 1:
            print(f"データ取得失敗: {symbol}")
            continue

        ticker = data["data"]
        all_data.append({
            "Time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": symbol.upper(),
            "Last": float(ticker["last"]),
            "High": float(ticker["high"]),
            "Low": float(ticker["low"]),
            "Bid": float(ticker["buy"]),
            "Ask": float(ticker["sell"]),
            "Volume": float(ticker["vol"])
        })

    # Excelファイルが既にあれば追記、なければ新規作成
    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path)
        df = pd.concat([df_existing, pd.DataFrame(all_data)], ignore_index=True)
    else:
        df = pd.DataFrame(all_data)

    df.to_excel(excel_path, index=False)
    print(f"{now} データ保存完了 → {excel_path}")

    time.sleep(interval)
