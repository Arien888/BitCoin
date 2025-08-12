import os
import yaml
import requests
import pandas as pd
import datetime as dt

# --- config.yaml 読み込み（1つ上の階層から） ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 保存先パス取得（相対パス→絶対パス）
excel_rel_path = config["paths"]["asset_excel"]
excel_abs_path = os.path.abspath(os.path.join(BASE_DIR, "..", excel_rel_path))

# --- Bitgetリアルタイム価格APIエンドポイント ---
symbol = "btc_usdt"
url = f"https://api.bitget.com/api/spot/v1/market/ticker?symbol={symbol}"

response = requests.get(url)
data = response.json()

if data.get("code") == "00000":  # 正常レスポンス確認（Bitget API仕様）
    ticker = data.get("data", {})
    price = float(ticker.get("last", 0))
    timestamp = dt.datetime.now()

    # データフレーム作成
    df = pd.DataFrame([{
        "Datetime": timestamp,
        "Symbol": symbol.upper(),
        "Price": price,
    }])

    # Excelに保存（追記モード）
    if os.path.exists(excel_abs_path):
        existing_df = pd.read_excel(excel_abs_path)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_excel(excel_abs_path, index=False)
    print(f"✅ 価格をExcelに保存しました: {excel_abs_path}")
else:
    print(f"APIエラー: {data}")
