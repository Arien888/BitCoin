import yaml
import ccxt
import pandas as pd

# config.yaml を読み込む
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config["mexc"]["apiKey"]
secret = config["mexc"]["secret"]

# ccxt.mexc のインスタンス作成（先物モード）
exchange = ccxt.mexc(
    {
        "apiKey": api_key,
        "secret": secret,
        "enableRateLimit": True,
        "options": {
            "defaultType": "swap",  # 先物(スワップ)を使う
        },
    }
)

try:
    positions = exchange.fetch_positions()

    # DataFrame化（複数ポジション対応のため）
    df = pd.DataFrame(positions)

    # Excelに書き込み
    excel_file = "mexc_positions.xlsx"
    df.to_excel(excel_file, index=False)

    print(f"ポジション情報を'{excel_file}'に保存しました。")

except Exception as e:
    print("Error:", e)
