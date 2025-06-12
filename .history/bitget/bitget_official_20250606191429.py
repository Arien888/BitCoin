import time
import requests
import hmac
import hashlib
import base64
import yaml
from urllib.parse import urlencode


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def sign_request(api_secret, method, request_path, timestamp, body=""):
    """
    Bitget API署名生成
    """
    message = timestamp + method.upper() + request_path + body
    hmac_key = base64.b64decode(api_secret)
    signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def get_margin_accounts(api_key, api_secret, passphrase):
    base_url = "https://api.bitget.com"
    method = "GET"
    request_path = "/api/mix/v1/account/accounts"
    timestamp = str(int(time.time() * 1000))
    body = ""

    signature = sign_request(api_secret, method, request_path, timestamp, body)

    headers = {
        "Content-Type": "application/json",
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
    }

    url = base_url + request_path
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    config = load_config()

    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]

    accounts_info = get_margin_accounts(api_key, api_secret, api_passphrase)
    print(accounts_info)


if __name__ == "__main__":
    main()
