import requests
import datetime as dt

symbols = [
    "btc_jpy",
    "eth_jpy",
    "xrp_jpy",
]

def load_config():
    # main.py の1つ上の階層にconfig.yamlがある想定
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

now = dt.datetime.now()
prices = []

for symbol in symbols:
    url = f"https://public.bitbank.cc/{symbol}/ticker"
    try:
        response = requests.get(url)
        res_json = response.json()
        if res_json.get("success", False):
            last_price = float(res_json["data"]["last"])
            prices.append((symbol.upper(), last_price))
        else:
            print(f"APIエラー: {symbol} - {res_json}")
    except Exception as e:
        print(f"取得失敗: {symbol} - {e}")

print(f"=== {now} 現在価格 ===")
for sym, price in prices:
    print(f"{sym}: {price}")
