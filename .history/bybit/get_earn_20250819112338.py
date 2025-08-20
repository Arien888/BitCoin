import time
import hmac
import hashlib
import requests
from load_config import load_config

config = load_config()
api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

def get_total_balance():
    url = "https://api.bybit.com/v5/asset/account"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    body_str = ""  # GETなので空文字

    # 署名作成
    origin_string = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(api_secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 200:
        data = response.json()
        if data.get("retCode") == 0:
            return data.get("result", {}).get("list", [])
        else:
            print(f"Error: {data.get('retMsg')}")
    else:
        print(f"HTTP Error: {response.status_code}")
    return None

# --- 実行 ---
balances = get_total_balance()
if balances:
    for asset in balances:
        print(asset)
