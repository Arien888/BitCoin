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
    print("Earning資産取得ステータス:", response.status_code)
    return safe_json(response)

def redeem_earning(product_id, amount):
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
    response = requests.post(url, headers=headers, data=body)
    print(f"償還リクエスト: {product_id} {amount} → ステータス {response.status_code}")
    print(response.text)
    return safe_json(response)

def get_btc_price():
    """BTC/USDT 現在価格を取得"""
    url = f"{BASE_URL}/api/spot/v1/market/ticker?symbol=BTCUSDT"
    response = requests.get(url)
    data = safe_json(response)
    if data and "data" in data and len(data["data"]) > 0:
        return float(data["data"][0]["last"])
    else:
        print("BTC価格取得失敗")
        return None

if __name__ == "__main__":
    assets_data = get_earning_assets()
    if not assets_data or "data" not in assets_data:
        print("Earning資産取得失敗")
        exit()

    btc_price = get_btc_price()
    if btc_price is None:
        exit()

    for asset in assets_data["data"]:
        coin = asset.get("coin")
        available = float(asset.get("amount", 0))

        if coin == "BTC" and available > 0:
            print(f"BTC利用可能: {available} BTC")
            # 1USDT分のBTC量
            amount_per_usdt = 1 / btc_price
            # 小数点以下は最小償還単位0.00001BTCで調整
            min_unit = 0.00001
            amount_per_usdt = max(amount_per_usdt, min_unit)

            count = int(available / amount_per_usdt)
            print(f"BTCを1USDT分ずつ償還 → {count}回")

            for i in range(count):
                redeem_earning("BTC", round(amount_per_usdt, 8))
                time.sleep(1)  # API制限回避
