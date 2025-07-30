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


def generate_signature_v5(
    api_secret, timestamp, api_key, recv_window, method, endpoint, query_string=""
):
    # v5署名ルール：timestamp + api_key + recv_window + method + endpoint + query_string
    payload = f"{timestamp}{api_key}{recv_window}{method}{endpoint}{query_string}"
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
    sign = generate_signature_v5(
        api_secret,
        timestamp,
        api_key,
        recv_window,
        method,
        endpoint,
        f"?{query_string}" if query_string else "",
    )

    headers = {
        "X-BYBIT-API-KEY": api_key,
        "X-BYBIT-API-SIGN": sign,
        "X-BYBIT-API-TIMESTAMP": timestamp,
        "X-BYBIT-API-RECV-WINDOW": recv_window,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
