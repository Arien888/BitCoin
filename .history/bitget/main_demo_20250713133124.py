import json


from bitget_utils_demo import (
    load_config,
    get_assets,
    save_assets_to_csv_jp,
    write_to_existing_excel,
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
    api_key = config["bitget"]["api_key"]
    api_secret = config["bitget"]["api_secret"]
    api_passphrase = config["bitget"]["passphrase"]
    base_url = config["bitget"]["demo_urls"]["base"]
    excel_path = config["demo_bitget_excel"]["asset_excel"]
    request_path = config["bitget"]["demo_futures"]

    try:
        result = get_assets(
            api_key,
            api_secret,
            api_passphrase,
            base_url,
            request_path,
            product_type="umcbl",
        )
        keys = futures_position_keys
        print(
            f"取得したデータ: {json.dumps(result, indent=2, ensure_ascii=False)}"
        )  # 追加

        # ここでレスポンス中身を確認
        print(json.dumps(result, indent=2, ensure_ascii=False))  # 追加

        write_to_existing_excel(
            excel_path, result, keys, sheet_name="bitget_futures_demo"
        )

    except Exception as e:
        print(f"エラー発生（）: {e}")


if __name__ == "__main__":
    main()
