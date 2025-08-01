import json
import time
import hmac
import hashlib
import requests
from load_config import load_config

def cancel_all_orders(api_key, api_secret):
    url = "https://api.bybit.com/v5/order/cancel-all"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    body = {
        "category": "linear"  # ← USDT無期限先物
    }

    # ✅ 正しい JSON 文字列（スペースなし）
    body_str = json.dumps(body, separators=(",", ":"))
    sign_payload = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(
        api_secret.encode("utf-8"),
        sign_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature
    }

    response = requests.post(url, headers=headers, data=body_str)

    print("=== レスポンス ===")
    print(response.text)
    return response.json()

def main():
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]

    try:
        result = cancel_all_orders(api_key, api_secret)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ エラー発生: {e}")

if __name__ == "__main__":
    main()
