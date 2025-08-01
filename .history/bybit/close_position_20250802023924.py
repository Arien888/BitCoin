import time
import hmac
import hashlib
import requests
from load_config import load_config
import urllib.parse
import urllib.parse


def generate_signature(
    secret: str, timestamp: str, method: str, path: str, data=None
) -> str:
    """
    dataはGETならdictのクエリパラメータ、POSTならJSON文字列など。
    Noneなら空文字列扱い。
    """
    if data is None:
        body = ""
    elif isinstance(data, dict):
        # dictならURLエンコードする
        body = urllib.parse.urlencode(data)
    else:
        # 文字列ならそのまま使う
        body = data

    origin_string = f"{timestamp}{method.upper()}{path}{body}"

    print("===== DEBUG: 署名関数呼び出し =====")
    print(f"timestamp: {timestamp}")
    print(f"method: {method}")
    print(f"path: {path}")
    print(f"body: {body}")
    print(f"origin_string: {origin_string}")

    print(
        f"final return: {hmac.new(secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()}"
    )

    return hmac.new(secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()


def get_open_positions(api_key, api_secret):
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/v5/position/list"
    params = {"category": "linear", "apiKey": api_key}
    query_string = urllib.parse.urlencode(sorted(params.items()))
    sign = generate_signature(api_secret, timestamp, method, path, query_string)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": sign,
        "Content-Type": "application/json",
    }

    url = f"https://api.bybit.com{path}?{query_string}"

    response = requests.get(url, headers=headers)

    print("Status:", response.status_code)
    print("Body:", response.text)

    data = response.json()
    return data["result"]["list"]


def close_position(api_key, api_secret, symbol, side, qty):
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    path = "/v5/order/create"

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
