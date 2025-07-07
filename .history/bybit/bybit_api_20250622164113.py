import time
import hmac
import hashlib
import requests
import json


def generate_signature(
    secret: str, timestamp: str, method: str, path: str, body: str = ""
) -> str:
    origin_string = timestamp + method.upper() + path + body
    return hmac.new(secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()


def get_bybit_spot_assets(
    api_key: str, api_secret: str, base_url: str = "https://api.bybit.com"
):
    endpoint = "/v5/account/wallet-balance"  # ハイフンあり
    method = "GET"
    timestamp = str(int(time.time() * 1000))
    request_path = endpoint

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": "5000",
        "Content-Type": "application/json",
    }

    body = ""

    sign = generate_signature(api_secret, timestamp, method, request_path, body)
    headers["X-BAPI-SIGN"] = sign

    url = base_url + endpoint

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
