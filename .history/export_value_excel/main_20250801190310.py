import json
import time
import hmac
import hashlib
import requests
from load_config import load_config

def cancel_all_orders(api_key, api_secret, category="linear", symbol=None):
    url = "https://api.bybit.com/v5/order/cancel-all"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    body = {
        "category": category,
    }
    if symbol:
        body["symbol"] = symbol

    # ✅ 正しいシリアライズ形式
    body_str = json.dumps(body, separators=(",", ":"))
    message = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json",
    }

    # ✅ 正しい body 形式（body_str を使用）
    response = requests.post(url, headers=headers, data=body_str)

    print("=== レスポンス ===")
    print(response.text)
    return response.json()

def main():
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]

    try:
        result = cancel_all_orders(api_key, api_secret, category="linear")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ エラー発生: {e}")

if __name__ == "__main__":
    main()
