import json
from bybit_api import get_bybit_spot_assets
from load_config import load_config
import json
from bybit_api import get_bybit_spot_assets
from load_config import load_config
from write_excel import write_to_excel  # ここを追加

def main():
    config = load_config()
    api_key = config['bybit']['key']
    api_secret = config['bybit']['secret']
    excel_path = config['demo_bitget_excel']['asset_excel']
    try:
        result = get_bybit_spot_assets(api_key, api_secret)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        write_to_excel(result, excel_path)  # Excelに書き込む処理を追加
    except Exception as e:
        print(f"エラー発生（bybit_spot v3）: {e}")

if __name__ == "__main__":
    main()
