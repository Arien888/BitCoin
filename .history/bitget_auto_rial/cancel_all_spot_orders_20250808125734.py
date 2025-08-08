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
    elif not body:
        body = ""
    message = f"{timestamp}{method.upper()}{request_path}{body}"
    mac = hmac.new(
        api_secret.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256
    )
    return mac.hexdigest()


def get_open_orders(symbol):
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    request_path = f"/api/spot/v1/orders?symbol={symbol}&status=open"
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


if __name__ == "__main__":
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    for sym in symbols:
        orders_data = get_open_orders(sym)
        if orders_data.get("code") != "00000":
            print(f"{sym}の注文取得でエラー: {orders_data}")
            continue
        orders = orders_data.get("data", [])
        print(f"=== {sym} の未約定注文一覧 ===")
        print(json.dumps(orders, indent=2, ensure_ascii=False))
