import json
import time
import hmac
import hashlib
import requests
from load_config import load_config

def cancel_all_orders(api_key, api_secret, symbol=None):
    url = "https://api.bybit.com/v5/order/cancel-all"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    body = {"category": "linear"}
    if symbol:
        body["symbol"] = symbol

    body_json = json.dumps(body, separators=(",", ":"))
    sign_payload = f"{timestamp}{api_key}{recv_window}{body_json}"
    signature = hmac.new(api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
    }

    print(f"=== URL: {url}")
    print(f"=== Headers: {headers}")
    print(f"=== Body: {body_json}")
    print(f"=== Signature Payload: {sign_payload}")
    print(f"=== Signature: {signature}")

    response = requests.post(url, headers=headers, data=body_json)

    print("=== HTTP request info ===")
    print(response.request.method)
    print(response.request.url)
    print(response.request.headers)
    print(response.request.body)

    print("=== レスポンス ===")
    print(response.text)
    return response.json()

def main():
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]

    cancel_all_orders(api_key, api_secret, symbol="BTCUSDT")

if __name__ == "__main__":
    main()
