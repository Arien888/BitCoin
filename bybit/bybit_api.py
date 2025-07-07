import time
import hmac
import hashlib
import requests
import json


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


def generate_signature_v3(secret, params):
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hmac.new(
        bytes(secret, "utf-8"), bytes(sorted_params, "utf-8"), hashlib.sha256
    ).hexdigest()


def get_bybit_spot_assets(api_key, api_secret, base_url="https://api.bybit.com"):
    endpoint = "/spot/v1/account"
    url = base_url + endpoint

    timestamp = int(time.time() * 1000)
    params = {
        "api_key": api_key,
        "timestamp": timestamp,
        "recvWindow": 5000,
    }

    # 署名追加
    sign = generate_signature_v3(api_secret, params)
    params["sign"] = sign

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
