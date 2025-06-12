import requests
import time
import hmac
import hashlib
import yaml


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


import base64


def get_spot_accounts(api_key, api_secret, api_passphrase):
    base_url = "https://api.bitget.com"
    method = "GET"
    request_path = "/api/v2/spot/account/assets"
    timestamp = str(int(time.time() * 1000))
    query_string = ""  # GETなのでパラメータなし
    prehash = timestamp + api_key + timestamp  # V2ではこの順で結合

    # HMAC-SHA256署名（大文字の16進数にする必要あり）
    signature = (
        hmac.new(api_secret.encode(), prehash.encode(), hashlib.sha256)
        .hexdigest()
        .upper()
    )

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
        "locale": "en-US",
    }

    url = base_url + request_path
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(response.text)

    return response.json()


def main():
    config = load_config()

    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]
    result = get_spot_accounts(api_key, api_secret, api_passphrase)
    print(result)


if __name__ == "__main__":
    main()
