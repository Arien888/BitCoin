import json


from bitget_utils import (
    load_config_2,
    get_assets,
    save_assets_to_csv_jp,
    write_to_existing_excel,
    get_futures_eccout_equity,
    get_futures_account,
    get_futures_positions,
    convert_futures_positions_to_assets_format,
)
from bitget_keys import (
    spot_keys,
    margin_keys,
    earn_keys,
    futures_keys,
    futures_position_keys,
)


def main():
    config = load_config_2()
    api_key = config["bitget_Unified"]["api_key"]
    api_secret = config["bitget_Unified"]["api_secret"]
    api_passphrase = config["bitget_Unified"]["passphrase"]
    urls = config["bitget"]["urls"]
    excel_path = config["paths"]["asset_excel"]

    for asset_type, path in urls.items():
        print(f"取得中: {asset_type} 資産情報")
        try:
            if asset_type != "bitget_all_assets":
                continue  # 他はスキップ
            else:
                result = get_assets(api_key, api_secret, api_passphrase, path)
                if asset_type == "bitget_all_assets":
                    keys = spot_keys
                else:
                    keys = []

                # ここでレスポンス中身を確認
            print(json.dumps(result, indent=2, ensure_ascii=False))  # 追加

            write_to_existing_excel(excel_path, result, keys, sheet_name=asset_type)

        except Exception as e:
            print(f"エラー発生（{asset_type}）: {e}")


if __name__ == "__main__":
    main()
