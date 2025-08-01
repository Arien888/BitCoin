import time
import hmac
import hashlib
import requests
import json
from load_config import load_config


def generate_signature(api_secret, params: dict):
    params_str = "&".join([f"{key}={value}" for key, value in sorted(params.items())])
    return hmac.new(
        api_secret.encode("utf-8"), params_str.sha256("utf-8"), hashlib.sha256
    ).hexdigest()


def place_order(symbol, side, order_type, qty, price=None, time_in_force="GTC"):
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    url = "https://api.bybit.com/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    body = {
        "category": "linear",  # # USDT建てなら linear、USDCは inverse
        "symbol": symbol,
        "side": side,  # "Buy" or "Sell"
        "orderType": order_type,  # "Limit" or "Market"
        "qty": str(qty),
        "timeInForce": time_in_force,
    }
    if order_type == "Limit" and price is not None:
        body["price"] = f"{price:.10f}".rstrip("0").rstrip(".")
    body_str = json.dumps(body)  # スペースありの標準出力

    origin_string = f"{timestamp}{api_key}{recv_window}{body_str}"

    signature = hmac.new(
        api_secret.encode(), origin_string.encode(), hashlib.sha256
    ).hexdigest()

    print("===署名(signature)===")
    print(signature)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": "5000",
    }

    param_str = timestamp + api_key + "5000" + json.dumps(body, separators=(",", ":"))
    signature = hmac.new(
        api_secret.encode(), param_str.encode(), hashlib.sha256
    ).hexdigest()
    headers["X-BYPI-SIGN"] = signature
    headers["Content-Type"] = "application/json"

    response = requests.post(url, headers=headers, data=json.dumps(body))

    print("===レスポンス===")
    print(response.text)
    return response.json()


if __name__ == "__main__":

    # テスト用発注内容
    symbol = "1000PEPEUSDT"
    side = "Buy"
    order_type = "Limit"
    qty = 1000000  # 取引所の単位による
    price = 0.0108580

    result = place_order(symbol, side, order_type, qty, price)
    print(json.dumps(result, indent=2, ensure_ascii=False))
