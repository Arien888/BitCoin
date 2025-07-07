import openpyxl
import requests
import time
import hmac
import hashlib
import yaml
import os
from datetime import datetime

# パス設定
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # bitcoin/
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "orders.xlsx")
LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "order_log.txt")

# config.yaml 読み込み
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

apiKey = config["mexc"]["apiKey"]
secret = config["mexc"]["api_secret"]
BASE_URL = "https://contract.mexc.com"

# 署名関数
def sign_params(params, secret):
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

# 発注関数
def place_order(symbol, side, price, quantity, order_type):
    url = f"{BASE_URL}/api/v1/private/order/submit"
    timestamp = int(time.time() * 1000)
    side_num = 1 if side.upper() == "BUY" else 2
    type_num = 1 if order_type.upper() == "LIMIT" else 2

    params = {
        "api_key": apiKey,
        "req_time": timestamp,
        "symbol": symbol,
        "price": price if type_num == 1 else 0,
        "vol": quantity,
        "side": side_num,
        "type": type_num,
        "open_type": 1,
        "position_id": 0,
        "leverage": 10,
        "external_oid": f"oid_{timestamp}"
    }
    params["sign"] = sign_params(params, secret)
    res = requests.post(url, data=params)
    return res.json()

# ログ出力
def log_result(row, result):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] Order: {row} → Result: {result}\n")

# メイン処理
def main():
    wb = openpyxl.load_workbook(EXCEL_PATH)
    sheet = wb.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        symbol, side, price, quantity, order_type = row
        print(f"→ 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
        result = place_order(symbol, side, price, quantity, order_type)
        log_result(row, result)
        time.sleep(1)  # レート制限対策

if __name__ == "__main__":
    main()
