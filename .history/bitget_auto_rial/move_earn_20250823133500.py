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

def safe_json(response):
    try:
        return response.json()
    except Exception:
        print("JSON変換失敗:", response.text)
        return None

def get_earning_assets():
    """最新API: Earning資産一覧取得"""
    url = f"{BASE_URL}/api/v2/earn/account/assets"
    request_path = "/api/v2/earn/account/assets"
    method = "GET"
    timestamp = get_timestamp()
    sign = sign_bitget(api_secret, timestamp, method, request_path)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    print("ステータスコード:", response.status_code)
    print("レスポンス:", response.text)
    return safe_json(response)

def redeem_earning(product_id, amount):
    """最新API: 償還（Earning → スポット）"""
    url = f"{BASE_URL}/api/v2/earn/savings/redeem"
    request_path = "/api/v2/earn/savings/redeem"
    method = "POST"
    body_dict = {"productId": product_id, "amount": str(amount)}
    body = json.dumps(body_dict, separators=(",", ":"))
    timestamp = get_timestamp()
    sign = sign_bitget(api_secret, timestamp, method, request_path, body)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

    print(f"償還リクエスト: {product_id} {amount}")
    response = requests.post(url, headers=headers, data=body)
    print("ステータスコード:", response.status_code)
    print("レスポンス:", response.text)
    return safe_json(response)

if __name__ == "__main__":
    assets_data = get_earning_assets()
    if not assets_data or "data" not in assets_data:
        print("Earning資産取得失敗またはデータなし")
        exit()

    for asset in assets_data["data"]:
        product_id = asset.get("productId") or asset.get("id") or asset.get("coin")
        available = float(asset.get("amount", 0))

        if available >= 1:
            print(f"処理対象: {product_id} 利用可能={available}")

            # 1USDTずつ償還
            count = int(available)  # 小数切捨てで整数USDT単位
            for i in range(count):
                print(f"{product_id} 1USDT償還 {i+1}/{count}")
                redeem_earning(product_id, 1)
                time.sleep(1)  # API制限回避
        else:
            print(f"{product_id} 利用可能残高 {available} は1USDT未満のためスキップ")
