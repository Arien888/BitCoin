import time
import hmac
import hashlib
import requests
import json
import time
import hmac
import hashlib
import requests


def generate_signature(
    secret: str, timestamp: str, method: str, path: str, body: str = ""
) -> str:
    origin_string = timestamp + method.upper() + path + body

    print("===== DEBUG: 署名関数呼び出し =====")
    print(f"timestamp: {timestamp}")
    print(f"method: {method}")
    print(f"path: {path}")
    print(f"body: {body}")
    print(f"origin_string: {timestamp + method.upper() + path + body}")

    return hmac.new(secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()


import time
import hmac
import hashlib
import requests


def generate_signature(api_secret, payload):
    return hmac.new(
        api_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

def get_bybit_spot_assets(api_key, api_secret, base_url="https://api.bybit.com"):
    endpoint = "/v5/account/wallet-balance"
    url = base_url + endpoint

    method = "GET"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    params = {"accountType": "SPOT"}

    query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    payload = f"{timestamp}{recv_window}{method}{endpoint}{query_string}"

    # デバッグ出力
    print("=== DEBUG START ===")
    print(f"timestamp     : {timestamp}")
    print(f"recv_window   : {recv_window}")
    print(f"method        : {method}")
    print(f"endpoint      : {endpoint}")
    print(f"query_string  : {query_string}")
    print(f"署名対象文字列: {payload}")

    sign = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    print(f"生成された署名 : {sign}")
    print("===================")

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": sign,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
