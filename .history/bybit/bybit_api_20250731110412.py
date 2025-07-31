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
import base64
import requests
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


def rsa_sign(private_key_path: str, message: str) -> str:
    """RSA署名を生成"""
    with open(private_key_path, "r") as f:
        private_key = RSA.import_key(f.read())
    signer = PKCS1_v1_5.new(private_key)
    digest = SHA256.new(message.encode("utf-8"))
    signature = signer.sign(digest)
    return base64.b64encode(signature).decode()


def get_bybit_spot_assets(api_key: str, api_secret: str, base_url="https://api.bybit.com"):
    endpoint = "/v5/account/wallet-balance"
    recv_window = "5000"
    timestamp = str(int(time.time() * 1000))
    method = "GET"

    params = {"accountType": "UNIFIED"}
    query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    url = base_url + endpoint + "?" + query_string

    # ❗️ここが最重要
    origin_string = f"{timestamp}{api_key}{recv_window}{query_string}"

    print("=== DEBUG START ===")
    print(f"timestamp     : {timestamp}")
    print(f"api_key       : {api_key}")
    print(f"recv_window   : {recv_window}")
    print(f"method        : {method}")
    print(f"endpoint      : {endpoint}")
    print(f"query_string  : {query_string}")
    print(f"署名対象文字列: {origin_string}")

    signature = hmac.new(api_secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
