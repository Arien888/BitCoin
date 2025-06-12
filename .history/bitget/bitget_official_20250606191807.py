import requests
import time
import hmac
import hashlib
import yaml

def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_spot_accounts(api_key, api_secret, api_passphrase):
    base_url = "https://api.bitget.com"
    method = "GET"
    request_path = "/api/spot/v1/account/accounts"
    timestamp = str(int(time.time() * 1000))
    body = ""

    message = timestamp + method + request_path + body
    signature = hmac.new(
        api_secret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
    }

    url = base_url + request_path
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]
    result = get_spot_accounts(api_key, api_secret, api_passphrase)
    print(result)


if __name__ == "__main__":
    main()
