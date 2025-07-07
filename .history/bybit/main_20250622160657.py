import json
from bybit_api import get_bybit_spot_assets
from excel_utils import write_to_existing_excel
from load_config import load_config

def main():
    config = load_config()
    api_key = config['bybit']['key']
    api_secret = config['bybit']['secret']
    excel_path = config['paths']['asset_excel']

    try:
        result = get_bybit_spot_assets(api_key, api_secret)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if 'result' in result and 'list' in result['result']:
            balances = result['result']['list']
            filtered = [
                {
                    'coin': b['coin'],
                    'availableBalance': b['availableBalance'],
                }
                for b in balances
                if float(b.get('availableBalance', 0)) > 0
            ]
        else:
            filtered = []

        keys = ['coin', 'availableBalance']
        write_to_existing_excel(excel_path, filtered, keys, sheet_name='bybit_spot')

    except Exception as e:
        print(f"エラー発生（bybit_spot）: {e}")

if __name__ == "__main__":
    main()
