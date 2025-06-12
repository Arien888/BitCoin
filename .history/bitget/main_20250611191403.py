import requests
import time
import hmac
import hashlib
import base64
import json
import yaml
import csv


from bitget_utils import get_assets, save_assets_to_csv_jp


def main():
    config = load_config()
    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]
    urls = config["bitget"]["urls"]

    for asset_type, path in urls.items():
        print(f"取得中: {asset_type} 資産情報")
        try:
            result = get_assets(api_key, api_secret, api_passphrase, path)
            save_assets_to_csv_jp(f"{asset_type}_assets.csv", result)
        except Exception as e:
            print(f"エラー発生（{asset_type}）: {e}")


if __name__ == "__main__":
    main()
