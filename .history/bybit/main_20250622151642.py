import json
from binance_api import get_binance_account
from excel_utils import write_to_existing_excel
from load_config import load_config

def main():
    config = load_config()
    api_key = config['binance']['key']
    api_secret = config['binance']['secret']
    excel_path = config['paths']['asset_excel']

    try:
        result = get_binance_account(api_key, api_secret)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        balances = [b for b in result['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]

        keys = ['asset', 'free', 'locked']
        write_to_existing_excel(excel_path, balances, keys, sheet_name='binance_spot')

    except Exception as e:
        print(f"エラー発生（binance_spot）: {e}")

if __name__ == "__main__":
    main()
