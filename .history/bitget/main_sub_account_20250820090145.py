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

    # 👇 bitget_all_assets のみ処理
    asset_type = "bitget_all_assets"
    path = urls.get(asset_type)

    if not path:
        print("config.yaml に bitget_all_assets が見つかりません")
        return

    print(f"取得中: {asset_type} 資産情報")
    try:
        result = get_assets(api_key, api_secret, api_passphrase, path)
        keys = all_assets_keys  # ← bitget_all_assets 用のキー定義に合わせる

        print(json.dumps(result, indent=2, ensure_ascii=False))

        write_to_existing_excel(excel_path, result, keys, sheet_name=asset_type)

    except Exception as e:
        print(f"エラー発生（{asset_type}）: {e}")


if __name__ == "__main__":
    main()
