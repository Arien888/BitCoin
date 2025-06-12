import requests
import time
import hmac
import hashlib
import base64
import yaml
import csv


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_assets(api_key, api_secret, api_passphrase, request_path):
    base_url = "https://api.bitget.com"
    method = "GET"
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
        print(f"{filename}: 資産データがありません")
        return

    keys = ["coin", "available", "limitAvailable", "frozen", "locked", "uTime"]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(keys)
        for asset in assets:
            row = [asset.get(k, "") for k in keys]
            writer.writerow(row)

    print(f"{filename} にCSV出力しました")
