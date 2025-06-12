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
    request_path = "/api/v2/spot/account/assets"
    method = "GET"
    timestamp = str(int(time.time() * 1000))
    body = ""

    # ✅ 正しい署名フォーマット（V2）
    pre_sign_str = timestamp + method + request_path + body

    signature = hmac.new(
        api_secret.encode("utf-8"), pre_sign_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()

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

    # デバッグ出力
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

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
