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
        api_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def get_bybit_spot_assets(api_key, api_secret):
    endpoint = "/v5/account/wallet-balance"
    base_url = "https://api.bybit.com"
    url = base_url + endpoint

    method = "GET"
    timestamp = str(int(time.time() * 1000))
    params = {
        "accountType": "SPOT"
    }
    query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    payload = f"{timestamp}{api_key}5000{method}{endpoint}?{query_string}"

    signature = generate_signature(api_secret, payload)

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": "5000"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# 使用例
if __name__ == "__main__":
    from load_config import load_config
    import json

    config = load_config()
    api_key = config['bybit']['key']
    api_secret = config['bybit']['secret']

    try:
        result = get_bybit_spot_assets(api_key, api_secret)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"エラー発生（bybit_spot v3）: {e}")
