import json
from bitget_util import load_config, get_spot_accounts, save_assets_to_csv_jp


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
