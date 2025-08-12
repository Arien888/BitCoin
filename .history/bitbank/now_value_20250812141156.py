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

# ビットバンクの銘柄ペアリスト（JPYペア）
symbols = [
    "btc_jpy",
    "eth_jpy",
    "xrp_jpy",
    # 必要に応じて追加してください
]

records = []
now = dt.datetime.now()

for symbol in symbols:
    url = f"https://public.bitbank.cc/{symbol}/ticker"
    try:
        response = requests.get(url)
        res_json = response.json()
        if res_json.get("success", False):
            last_price = float(res_json["data"]["last"])
            records.append({
                "Datetime": now,
                "Symbol": symbol.upper(),
                "Price": last_price,
            })
        else:
            print(f"APIエラー: {symbol} - {res_json}")
    except Exception as e:
        print(f"取得失敗: {symbol} - {e}")

if records:
    df = pd.DataFrame(records)

    # 既存ファイルがあれば読み込み追記
    if os.path.exists(excel_abs_path):
        existing_df = pd.read_excel(excel_abs_path)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_excel(excel_abs_path, index=False)
    print(f"✅ 価格データをExcelに追記保存しました: {excel_abs_path}")
else:
    print("取得データがありませんでした。")
