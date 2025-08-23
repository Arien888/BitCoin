import time
import hmac
import hashlib
import base64
import requests
import json
import yaml
import os

# 設定読み込み
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["bitget"]["api_key"]
api_secret = config["bitget"]["api_secret"]
passphrase = config["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_bitget(api_secret, timestamp, method, request_path, body=""):
    message = f"{timestamp}{method.upper()}{request_path}{body}"
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def redeem_earning(asset, quantity):
    """Earning資産を償還してスポットに移動"""
    url = f"{BASE_URL}/api/earn/v1/redeem"
    request_path = "/api/earn/v1/redeem"
    method = "POST"
    body_dict = {
        "coin": asset.upper(),
        "amount": str(quantity)
    }
    body = json.dumps(body_dict, separators=(",", ":"))
    timestamp = get_timestamp()
    sign = sign_bitget(api_secret, timestamp, method, request_path, body)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=body)
    return response.json()

def get_earning_assets():
    """現在Earningに預けている資産一覧を取得"""
    url = f"{BASE_URL}/api/earn/v1/account/asset"
    request_path = "/api/earn/v1/account/asset"
    method = "GET"
    timestamp = get_timestamp()
    sign = sign_bitget(api_secret, timestamp, method, request_path)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
    }

    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    earning_assets = get_earning_assets()
    print("=== Earning資産一覧 ===")
    print(json.dumps(earning_assets, indent=2, ensure_ascii=False))

    # 例: 全資産償還
    for asset_info in earning_assets.get("data", []):
        coin = asset_info["coin"]
        amount = float(asset_info["available"])  # 利用可能残高
        if amount > 0:
            print(f"償還実行: {coin} → {amount}")
            result = redeem_earning(coin, amount)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            time.sleep(1)  # API制限回避
