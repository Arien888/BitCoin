import pandas as pd
import time
import requests
import hashlib
import hmac
import yaml
import os

# config.yaml 読み込み関数
def load_config():
    with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'r') as f:
        return yaml.safe_load(f)

config = load_config()
API_KEY = config['mexc']['api_key']
SECRET_KEY = config['mexc']['secret_key']
BASE_URL = 'https://contract.mexc.com'

def sign_request(params, secret):
    query_string = '&'.join(f"{k}={params[k]}" for k in sorted(params))
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(symbol, price, vol, side):
    url = BASE_URL + "/api/v1/private/order/submit"
    ts = int(time.time() * 1000)

    data = {
        "api_key": API_KEY,
        "req_time": ts,
        "symbol": symbol,
        "price": float(price),
        "vol": float(vol),
        "side": 1 if side.lower() == 'buy' else 2,
        "type": 1,        # 指値注文
        "open_type": 1,   # クロスマージン
        "position_id": 0,
        "lever": 3,
        "external_oid": str(ts),
    }
    data["sign"] = sign_request(data, SECRET_KEY)

    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        resp_json = res.json()
        print(f"Order {symbol} {side} {vol}@{price} → {resp_json}")
        return resp_json
    except Exception as e:
        print(f"Order failed: {symbol} {side} {vol}@{price} → {e}")
        return None

def main():
    # orders.xlsx は run_all.py と同じディレクトリに置く想定
    excel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'orders.xlsx'))
    df = pd.read_excel(excel_path)

    for idx, row in df.iterrows():
        symbol = row.get('Symbol')
        side = row.get('Side')
        price = row.get('Price')
        quantity = row.get('Quantity')

        if not all([symbol, side, price, quantity]):
            print(f"Skipping row {idx+1} due to missing data")
            continue

        place_order(symbol, price, quantity, side)
        time.sleep(0.5)  # API過負荷防止

if __name__ == "__main__":
    main()
