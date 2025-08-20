import time
import hmac
import hashlib
import requests
from load_config import load_config

# --- config 読み込み ---
config = load_config()
api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

def get_earn_balance(account_type="SPOT", coin=None):
    url = "https://api.bybit.com/v5/asset/transfer/query-account-coins-balance"
    params = {"accountType": account_type}
    if coin:
        params["coin"] = coin.upper()

    # GET の場合は bodyStr を空文字にする
    body_str = ""
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    # 署名生成
    origin_string = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(api_secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    # デバッグ用にステータスとレスポンスを表示
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 200:
        try:
            data = response.json()
            if data.get("retCode") == 0:
                return data.get("result", {}).get("list", [])
            else:
                print(f"Error: {data.get('retMsg')}")
        except Exception as e:
            print(f"JSON decode error: {e}")
    else:
        print(f"HTTP Error: {response.status_code}")
    return None

# --- 使用例 ---
balances = get_earn_balance(coin="USDT")
if balances:
    for balance in balances:
        print(balance)
