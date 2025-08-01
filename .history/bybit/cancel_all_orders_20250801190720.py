import json
import time
import hmac
import hashlib
import requests
from load_config import load_config  # あなたの環境に合わせてAPIキー読み込み関数

def cancel_all_orders(api_key, api_secret):
    url = "https://api.bybit.com/v5/order/cancel-all"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    # 必須パラメータ
    body = {
        "category": "linear"  # USDT無期限先物。USD建て先物は"inverse"
    }

    # JSONをスペースなしで整形（署名対象と一致させるため）
    body_json = json.dumps(body, separators=(",", ":"))
    sign_payload = f"{timestamp}{api_key}{recv_window}{body_json}"

    # HMAC-SHA256署名生成
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

    response = requests.post(url, headers=headers, data=body_json)

    print("=== レスポンス ===")
    print(response.text)
    return response.json()

def main():
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]

    result = cancel_all_orders(api_key, api_secret)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
