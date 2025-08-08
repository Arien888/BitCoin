import time
import hmac
import hashlib
import requests
import json
import os
import yaml

# スクリプトのあるディレクトリ（どこから実行されても同じになる）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# config.yaml の読み込み
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

    # ======== APIキー設定 ========
api_key = config["bitget"]["api_key"]
api_secret = config["bitget"]["api_secret"]
passphrase = config["bitget"]["passphrase"]

# ======== エンドポイント ========
BASE_URL = "https://api.bitget.com"
CANCEL_ALL_ORDERS_PATH = "/api/v3/trade/cancel-symbol-order"


# ======== 署名作成関数 ========
def sign(timestamp, method, request_path, body=""):
    if body and isinstance(body, dict):
        body = json.dumps(body, separators=(",", ":"))
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        api_secret.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256
    )
    return mac.hexdigest()


# ======== リクエスト送信関数 ========
def cancel_all_spot_orders():
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    body = {"category": "SPOT"}  # symbol省略でSPOT全キャンセル

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


# ======== 実行 ========
if __name__ == "__main__":
    result = cancel_all_spot_orders()
    print(json.dumps(result, indent=2, ensure_ascii=False))
