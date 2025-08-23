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
TARGET_COIN = "SOL"       # 償還対象コイン
AMOUNT_PER_REDEEM = 0.5   # 1回あたり償還量（SOL単位）
MIN_UNIT = 0.01           # SOLの最小償還単位
SLEEP_SEC = 1             # API制限回避のウェイト

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
    sign = sign_bitget(API_SECRET, timestamp, method, request_path, body)
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=body)
    print(f"償還リクエスト: {product_id} {amount} → ステータス {response.status_code}")
    print(response.text)
    return safe_json(response)

# =========================
# 実行処理
# =========================
if __name__ == "__main__":
    assets_data = get_earning_assets()
    if not assets_data or "data" not in assets_data:
        print("Earning資産取得失敗")
        exit()

    for asset in assets_data["data"]:
        coin = asset.get("coin")
        available = float(asset.get("amount", 0))

        if coin == TARGET_COIN and available > 0:
            print(f"{TARGET_COIN} 利用可能: {available} {TARGET_COIN}")

            # 償還量を最小単位で調整
            redeem_amount = max(AMOUNT_PER_REDEEM, MIN_UNIT)
            count = int(available / redeem_amount)
            print(f"{TARGET_COIN} を{AMOUNT_PER_REDEEM}{TARGET_COIN}ずつ償還 → {count}回")

            for i in range(count):
                redeem_earning(TARGET_COIN, round(redeem_amount, 8))
                time.sleep(SLEEP_SEC)  # API制限回避
