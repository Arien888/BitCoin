import time
import hmac
import hashlib
import requests
import json
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["bitget"]["api_key"]
api_secret = config["bitget"]["api_secret"]
passphrase = config["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"

def sign(timestamp, method, request_path, body=""):
    if body and isinstance(body, dict):
        body = json.dumps(body, separators=(",", ":"))
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        api_secret.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256
    )
    return mac.hexdigest()

def get_open_orders(symbol):
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    request_path = f"/api/spot/v1/open_orders?symbol={symbol}"
    body = ""
    signature = sign(timestamp, method, request_path, body)
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
    }
    url = BASE_URL + request_path
    res = requests.get(url, headers=headers)
    return res.json()

def cancel_order(symbol, order_id):
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    request_path = "/api/spot/v1/cancel_order"
    body = {
        "symbol": symbol,
        "orderId": order_id,
    }
    signature = sign(timestamp, method, request_path, body)
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }
    url = BASE_URL + request_path
    res = requests.post(url, headers=headers, data=json.dumps(body))
    return res.json()

if __name__ == "__main__":
    # 全注文キャンセルしたいシンボルのリスト
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]  # 必要に応じて増やしてください

    for sym in symbols:
        orders_data = get_open_orders(sym)
        if orders_data.get("code") != "00000":
            print(f"{sym}の注文取得でエラー: {orders_data}")
            continue
        orders = orders_data.get("data", [])
        for order in orders:
            order_id = order.get("orderId") or order.get("order_id")  # API応答で変わる可能性あり
            if not order_id:
                continue
            cancel_result = cancel_order(sym, order_id)
            print(f"キャンセル注文ID {order_id} シンボル {sym} 結果: {cancel_result}")
