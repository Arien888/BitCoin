import time
import hmac
import hashlib
import requests
from load_config import load_config
import urllib.parse
import urllib.parse


def generate_signature(
    secret: str, api_key: str, timestamp: str, method: str, recv_window: int, data=None
) -> str:

    # パラメータをアルファベット順にソートしURLエンコード
    sorted_params_str = urllib.parse.urlencode(sorted(data.items()))

    # origin_stringを生成
    origin_string = f"{timestamp}{api_key}{recv_window}{sorted_params_str}"

    print(f"timestamp: {timestamp} ({type(timestamp)})")
    print(f"api_key: {api_key} ({type(api_key)})")
    print(f"recv_window: {recv_window} ({type(recv_window)})")
    print(f"sorted_params_str: {sorted_params_str}")
    origin_string = f"{timestamp}{api_key}{str(recv_window)}{sorted_params_str}"
    print(f"origin_string: {origin_string}")

    # HMAC-SHA256で署名を生成
    signature = hmac.new(
        secret.encode(), origin_string.encode(), hashlib.sha256
    ).hexdigest()

    return signature


def get_open_positions(api_key, api_secret):
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/v5/position/list"
    recv_window = "5000"  # 5秒
    params = {
        "category": "linear",  # ←これを含める
        "timestamp": timestamp,
        "recv_window": recv_window,
    }
    query_string = urllib.parse.urlencode(sorted(params.items()))
    sign = generate_signature(
        secret=api_secret,
        timestamp=str(timestamp),
        method="GET",
        path="/v5/position/list",
        data=params,
    )

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": sign,
        "Content-Type": "application/json",
    }

    url = f"https://api.bybit.com{path}?{query_string}"

    print("\n=== [get_open_positions] リクエスト情報 ===")
    print("URL:", url)
    print("Headers:", headers)

    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    try:
        data = response.json()
        print("Parsed JSON:", data)
    except Exception as e:
        print("JSON decode error:", e)
        raise

    if data.get("retCode") != 0:
        raise Exception(f"APIエラー: {data.get('retMsg')}")

    return data["result"]["list"]


def close_position(api_key, api_secret, symbol, side, qty):
    timestamp = str(int(time.time() * 1000))
    method = ("GET",)
    path = ("/v5/position/list",)

    body_dict = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty),
    }
    import json

    body = json.dumps(body_dict)

    # 署名はJSON文字列のbodyを渡す
    sign = generate_signature(api_secret, timestamp, method, path, body)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": sign,
        "Content-Type": "application/json",
    }

    response = requests.post("https://api.bybit.com" + path, headers=headers, data=body)
    print(f"[{symbol}] クローズ結果:", response.json())


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
