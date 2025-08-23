import time
import hmac
import hashlib
import base64
import requests
import json
import yaml
import os

# =========================
# 設定
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

API_KEY = config["bitget"]["api_key"]
API_SECRET = config["bitget"]["api_secret"]
PASSPHRASE = config["bitget"]["passphrase"]
BASE_URL = "https://api.bitget.com"

# 償還設定
TARGET_COIN = "SOL"
AMOUNT_PER_REDEEM = 0.5
PERIOD_TYPE = "flexible"  # flexible か fixed


# =========================
# 関数
# =========================
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
    sign = sign_bitget(API_SECRET, timestamp, method, request_path)
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    print("Earning資産取得ステータス:", response.status_code)
    data = safe_json(response)
    if data and "data" in data:
        for asset in data["data"]:
            print("coin:", asset.get("coin"), "amount:", asset.get("amount"))
    return data


def get_earning_product_id(coin):
    url = f"{BASE_URL}/api/v2/earn/savings/product?coin={coin}&filter=available_and_held"
    request_path = f"/api/v2/earn/savings/product?coin={coin}&filter=available_and_held"
    method = "GET"
    timestamp = get_timestamp()
    sign = sign_bitget(API_SECRET, timestamp, method, request_path)
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    print("Earning商品取得ステータス:", response.status_code)
    print("レスポンス:", response.text)
    data = safe_json(response)
    if data and "data" in data:
        for item in data["data"]:
            if item.get("coin") == coin and item.get("periodType").lower() == PERIOD_TYPE:
                return item.get("productId")
    return None


def redeem_earning(product_id, amount, period_type="flexible"):
    url = f"{BASE_URL}/api/v2/earn/savings/redeem"
    request_path = "/api/v2/earn/savings/redeem"
    method = "POST"
    body_dict = {"productId": product_id, "amount": str(amount), "periodType": period_type}
    body = json.dumps(body_dict, separators=(",", ":"))
    timestamp = get_timestamp()
    sign = sign_bitget(API_SECRET, timestamp, method, request_path, body)
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=body)
    print(f"償還リクエスト: {product_id} {amount} → ステータス {response.status_code}")
    print(response.text)
    return safe_json(response)


# =========================
# 実行処理（1回だけ償還）
# =========================
if __name__ == "__main__":
    assets_data = get_earning_assets()
    if not assets_data or "data" not in assets_data:
        print("Earning資産取得失敗")
        exit()

    for asset in assets_data["data"]:
        coin = asset.get("coin")
        available = float(asset.get("amount", 0))

        if coin == TARGET_COIN and available >= AMOUNT_PER_REDEEM:
            product_id = get_earning_product_id(TARGET_COIN)
            if product_id:
                print(f"{TARGET_COIN} 利用可能: {available} {TARGET_COIN}, productId: {product_id}")
                redeem_earning(product_id, AMOUNT_PER_REDEEM, period_type=PERIOD_TYPE)
            else:
                print(f"{TARGET_COIN} の productId が取得できませんでした")
            break
