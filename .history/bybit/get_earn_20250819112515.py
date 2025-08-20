import time
import hmac
import hashlib
import requests
from load_config import load_config

config = load_config()
api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

def get_earn_balance():
    url = "https://api.bybit.com/v5/earn/account"  # 最新APIの残高取得エンドポイント
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    body_str = ""  # GET なら空文字

    # 署名作成
    signature = hmac.new(
        api_secret.encode(),
        f"{timestamp}{api_key}{recv_window}{body_str}".encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 200:
        data = response.json()
        if data.get("retCode") == 0:
            return data.get("result", {}).get("list", [])
        else:
            print("Error:", data.get("retMsg"))
    else:
        print("HTTP Error:", response.status_code)
    return None

balances = get_earn_balance()
if balances:
    for b in balances:
        print(b)
