import requests
import time
import hmac
import hashlib
import base64
import json


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_spot_accounts(api_key, api_secret, api_passphrase):
    base_url = "https://api.bitget.com"
    method = "GET"
    request_path = "/api/v2/spot/account/assets"
    timestamp = str(int(time.time() * 1000))
    query_string = ""  # クエリパラメータがある場合はここに追加
    body = ""  # GETリクエストの場合、ボディは空文字列

    # メッセージの構築
    if query_string:
        prehash_string = timestamp + method + request_path + "?" + query_string + body
    else:
        prehash_string = timestamp + method + request_path + body

        # HMAC SHA256による署名の生成
    signature = hmac.new(
        api_secret.encode("utf-8"), prehash_string.encode("utf-8"), hashlib.sha256
    ).digest()
    signature_base64 = base64.b64encode(signature).decode()

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature_base64,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
        "locale": "en-US",
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
    result = get_spot_accounts(api_key, api_secret, api_passphrase)
    print(result)


if __name__ == "__main__":
    main()
