import time
import hmac
import hashlib
import requests
from load_config import load_config


def generate_signature(params, secret):
    param_str = "&".join(f"{k}={params[k]}" for k in sorted(params))
    return hmac.new(
        secret.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_open_positions(api_key, api_secret):
    url = "https://api.bybit.com/v5/position/list"
    params = {
        "category": "linear",
        "timestamp": str(int(time.time() * 1000)),
        "apiKey": api_key,
    }
    sign = generate_signature(params, api_secret)
    params["sign"] = sign

    response = requests.get(url, params=params)
    data = response.json()

    print("=== API Response ===")
    print(response.status_code)
    print(response.text)
    print("====================")

    return data["result"]["list"]


def close_position(api_key, api_secret, symbol, side, qty):
    url = "https://api.bybit.com/v5/order/create"
    params = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty),
        "reduceOnly": "true",
        "timestamp": str(int(time.time() * 1000)),
        "apiKey": api_key,
    }
    sign = generate_signature(params, api_secret)
    params["sign"] = sign

    response = requests.post(url, data=params)
    print(f"[{symbol}] クローズ結果: {response.json()}")


def main():
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]

    try:
        positions = get_open_positions(api_key, api_secret)

        for pos in positions:
            size = float(pos["size"])
            if size == 0:
                continue  # ポジションなし

            symbol = pos["symbol"]
            side = pos["side"]  # "Buy" or "Sell"
            close_side = "Sell" if side == "Buy" else "Buy"

            print(f"[{symbol}] {side}ポジション({size}) → {close_side}成行で決済")
            close_position(api_key, api_secret, symbol, close_side, size)
            time.sleep(0.2)  # API制限対策

    except Exception as e:
        print(f"エラー発生（bybit_futures 全クローズ）: {e}")


if __name__ == "__main__":
    main()
