import yaml
import ccxt
import pandas as pd

# config.yaml読み込み
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config["mexc"]["apiKey"]
secret = config["mexc"]["secret"]

# 先物用インスタンス（swap）
exchange_swap = ccxt.mexc(
    {
        "apiKey": api_key,
        "secret": secret,
        "enableRateLimit": True,
        "options": {"defaultType": "swap"},
    }
)

# 現物用インスタンス（spot）
exchange_spot = ccxt.mexc(
    {
        "apiKey": api_key,
        "secret": secret,
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    }
)

try:
    # 先物ポジション取得
    positions = exchange_swap.fetch_positions()
    df_positions = pd.DataFrame(positions)

    # 現物残高取得
    balance = exchange_spot.fetch_balance()
    spot_balances = balance['total']
    filtered_spot = {k: v for k, v in spot_balances.items() if v and v > 0}
    df_spot = pd.DataFrame(list(filtered_spot.items()), columns=["通貨", "保有量"])

    # Excelファイルに別シートで書き込み
    excel_file = "mexc_positions_and_spot.xlsx"
    with pd.ExcelWriter(excel_file) as writer:
        df_positions.to_excel(writer, sheet_name="先物ポジション", index=False)
        df_spot.to_excel(writer, sheet_name="現物保有残高", index=False)

    print(f"先物ポジションと現物保有残高を'{excel_file}'に保存しました。")

except Exception as e:
    print("Error:", e)
