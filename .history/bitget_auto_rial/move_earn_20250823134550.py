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
PERIOD_TYPE = "FLEXIBLE"  # 'FLEXIBLE' または 'FIXED'


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


# 1. Earning商品一覧から productId を取得
def get_earning_products(coin):
    url = f"{BASE_URL}/api/v2/earn/savings/products"
    request_path = "/api/v2/earn/savings/products"
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
    data = safe_json(response)
    if not data or "data" not in data:
        print("Earning商品取得失敗")
        return None

    # coin と periodType が一致する商品の productId を返す（FLEXIBLE優先）
    for item in data["data"]:
        if item.get("coin") == coin and item.get("periodType") == PERIOD_TYPE:
            return item.get("productId")
    return None


# 2. 償還リクエスト
def redeem_earning(product_id, amount, period_type="FLEXIBLE"):
    url = f"{BASE_URL}/api/v2/earn/savings/redeem"
    request_path = "/api/v2/earn/savings/redeem"
    method = "POST"
    body_dict = {
        "productId": product_id,
        "amount": str(amount),
        "periodType": period_type,
    }
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
# 実行処理
# =========================
if __name__ == "__main__":
    # 1. SOL の productId を取得
    product_id = get_earning_products(TARGET_COIN)
    if not product_id:
        print(f"{TARGET_COIN} の productId が取得できませんでした")
        exit()

    print(f"{TARGET_COIN} の productId: {product_id}")

    # 2. 償還実行（1回だけ）
    redeem_earning(product_id, AMOUNT_PER_REDEEM, period_type=PERIOD_TYPE)
