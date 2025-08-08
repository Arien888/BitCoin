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
# クラシック現物アカウントの全注文キャンセルの仮のパス
CANCEL_ALL_ORDERS_PATH = "/api/spot/v1/cancel_order"

def sign(timestamp, method, request_path, body=""):
    if body and isinstance(body, dict):
        body = json.dumps(body, separators=(",", ":"))
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        api_secret.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256
    )
    return mac.hexdigest()

def cancel_all_spot_orders():
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    # symbolなしで全キャンセルできるAPIがあれば空、なければ全symbol指定が必要
    body = {}  # または { "symbol": "" } などAPI仕様に合わせて

    signature = sign(timestamp, method, CANCEL_ALL_ORDERS_PATH, body)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    response = requests.post(
        BASE_URL + CANCEL_ALL_ORDERS_PATH, headers=headers, data=json.dumps(body)
    )
    return response.json()

if __name__ == "__main__":
    result = cancel_all_spot_orders()
    print(json.dumps(result, indent=2, ensure_ascii=False))
