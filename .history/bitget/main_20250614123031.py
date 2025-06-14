import requests
import time
import hmac
import hashlib
import base64
import json
import yaml
import csv


from bitget_utils import load_config, get_assets, save_assets_to_csv_jp


spot_keys = ["coin", "available", "limitAvailable", "frozen", "locked", "uTime"]
margin_keys = [
    "coin",
    "totalAmount",
    "available",
    "frozen",
    "borrow",
    "interest",
    "net",
    "coupon",
    "cTime",
    "uTime",
]
earn_keys = ["coin", "amount"]
futures_keys = [
    "coin",
    "equity",
    "available",
    "locked",
    "unrealizedPnl",  # Lとlの違いに注意
]


def main():
    config = load_config()
    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]
    urls = config["bitget"]["urls"]

    for asset_type, path in urls.items():
        print(f"取得中: {asset_type} 資産情報")
        try:
            if asset_type == "futures":
                # 先物だけ productType パラメータを指定
                result = get_assets(
                    api_key,
                    api_secret,
                    api_passphrase,
                    path,
                    product_type="USDT-FUTURES",
                )
                keys = futures_keys
            else:
                result = get_assets(api_key, api_secret, api_passphrase, path)
                if asset_type == "spot":
                    keys = spot_keys
                elif asset_type == "margin":
                    keys = margin_keys
                elif asset_type == "earn":
                    keys = earn_keys
                else:
                    keys = []

            save_assets_to_csv_jp(f"{asset_type}_assets.csv", result, keys)
        except Exception as e:
            print(f"エラー発生（{asset_type}）: {e}")


def get_assets(api_key, api_secret, api_passphrase, path, product_type=None):
    base_url = "https://api.bitget.com"
    url = base_url + path

    timestamp = str(int(time.time() * 1000))
    method = "GET"
    request_path = path
    if product_type:
        request_path += f"?productType={product_type}"

    message = timestamp + method + request_path
    signature = hmac.new(
        api_secret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": api_passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }

    params = {"productType": product_type} if product_type else None

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["data"]


if __name__ == "__main__":
    main()
