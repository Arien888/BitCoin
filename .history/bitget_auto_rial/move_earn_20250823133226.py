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

def get_earning_assets():
    """Earning資産一覧を取得（デバッグ強化版）"""
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

    print("=== GET Earning資産 ===")
    print("URL:", url)
    print("Headers:", headers)
    print("Request Path:", request_path)
    print("Timestamp:", timestamp)

    response = requests.get(url, headers=headers)

    print("ステータスコード:", response.status_code)
    print("レスポンスヘッダー:", response.headers)
    print("レスポンス内容:", response.text)

    try:
        data = response.json()
        print("JSON変換成功:", json.dumps(data, indent=2, ensure_ascii=False))
        return data
    except Exception as e:
        print("JSON変換失敗:", e)
        return None

if __name__ == "__main__":
    earning_assets = get_earning_assets()
    if earning_assets:
        for asset_info in earning_assets.get("data", []):
            coin = asset_info.get("coin")
            available = asset_info.get("available")
            print(f"{coin}: 利用可能残高={available}")
