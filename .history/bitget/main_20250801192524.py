import json


from bitget_utils import (
    load_config,
    get_assets,
    save_assets_to_csv_jp,
    write_to_existing_excel,
    get_futures_eccout_equity,
)
from bitget_keys import (
    spot_keys,
    margin_keys,
    earn_keys,
    futures_keys,
    futures_position_keys,
)


def main():
    config = load_config()
    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]
    urls = config["bitget"]["urls"]
    excel_path = config["paths"]["asset_excel"]

    for asset_type, path in urls.items():
        print(f"取得中: {asset_type} 資産情報")
        try:
            if asset_type == "bitget_futures":
                # 先物だけ productType パラメータを指定
                result = get_assets(
                    api_key,
                    api_secret,
                    api_passphrase,
                    path,
                    product_type="USDT-FUTURES",
                )
                keys = futures_keys

                # 先物の総評価額を取得
                account_info = get_futures_eccout_equity(
                    api_key, api_secret, api_passphrase
                )

                print(
                    f"先物総評価額: {account_info.get('data', {}).get('equity', '取得失敗')}"
                )

            elif asset_type == "bitget_futures_positions":
                result = get_assets(
                    api_key,
                    api_secret,
                    api_passphrase,
                    path,
                    product_type="USDT-FUTURES",
                )
                keys = futures_position_keys

            else:
                result = get_assets(api_key, api_secret, api_passphrase, path)
                if asset_type == "bitget_spot":
                    keys = spot_keys
                elif asset_type == "bitget_margin":
                    keys = margin_keys
                elif asset_type == "bitget_earn":
                    keys = earn_keys
                else:
                    keys = []

                # ここでレスポンス中身を確認
            print(json.dumps(result, indent=2, ensure_ascii=False))  # 追加

            write_to_existing_excel(excel_path, result, keys, sheet_name=asset_type)

        except Exception as e:
            print(f"エラー発生（{asset_type}）: {e}")


if __name__ == "__main__":
    main()
