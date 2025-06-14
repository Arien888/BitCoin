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
    "coin",  # 通貨名
    "equity",  # 資産価値（残高合計）
    "available",  # 利用可能残高
    "locked",  # 凍結資産
    "unrealizedPL",  # 未実現損益（pnl）
    "initialMargin",  # 必要初期証拠金
    "maintMargin",  # 必要維持証拠金
    "marginRatio",  # 証拠金率
    "marginBalance",  # 証拠金残高
    "maxWithdrawAmount",  # 最大出金可能額
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

                # ここでレスポンス中身を確認
            print(json.dumps(result, indent=2, ensure_ascii=False))  # 追加

            save_assets_to_csv_jp(f"{asset_type}_assets.csv", result, keys)
        except Exception as e:
            print(f"エラー発生（{asset_type}）: {e}")


if __name__ == "__main__":
    main()
