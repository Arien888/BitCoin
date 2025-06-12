import requests
import time
import hmac
import hashlib
import base64
import json
import yaml
import csv


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_spot_accounts(api_key, api_secret, api_passphrase):
    base_url = "https://api.bitget.com"
    method = "GET"
    request_path = "/api/v2/earn/account/assets"  # マージン口座の資産取得APIパス

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


def save_assets_to_csv_jp(filename, data):
    assets = data.get("data", [])

    if not assets:
        print("資産データがありません")
        return

    header_map = {
        "coin": "...",
        "available": "...",
        "limitAvailable": "...",
        "frozen": "...",
        "locked": "...",
        "uTime": "...",
    }

    keys = list(header_map.keys())
    headers = list(header_map.values())

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["coin", "available", "limitAvailable", "frozen", "locked", "uTime"]
        writer.writerow(header)  # 漢字のヘッダー
        for asset in assets:
            row = [asset.get(k, "") for k in keys]
            writer.writerow(row)

    print(f"{filename} にCSV出力しました")


# main関数内の最後に追加するイメージ
def main():
    config = load_config()

    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]

    result = get_spot_accounts(api_key, api_secret, api_passphrase)

    print(json.dumps(result, indent=4))

    save_assets_to_csv_jp("assets.csv", result)


if __name__ == "__main__":
    main()
