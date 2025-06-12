import requests
import time
import hmac
import hashlib
import base64
import yaml
import csv


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_spot_accounts(api_key, api_secret, api_passphrase):
    base_url = "https://api.bitget.com"
    method = "GET"
    request_path = "/api/v2/spot/account/assets"

    timestamp = str(int(time.time() * 1000))
    body = ""
    prehash_string = timestamp + method + request_path + body

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


def save_assets_to_csv_jp(filename, data):
    assets = data.get("data", [])

    if not assets:
        print("資産データがありません")
        return

    header_map = {
        "coin": "コイン",
        "available": "利用可能",
        "limitAvailable": "制限付き利用可能",
        "frozen": "凍結",
        "locked": "ロック済み",
        "uTime": "更新時刻",
    }

    keys = list(header_map.keys())
    headers = list(header_map.values())

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for asset in assets:
            row = [asset.get(k, "") for k in keys]
            writer.writerow(row)

    print(f"{filename} にCSV出力しました")
