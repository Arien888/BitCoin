import time
import hmac
import hashlib
import requests
import json

def get_earn_balance(api_key, api_secret, account_type="SPOT", coin=None):
    url = "https://api.bybit.com/v5/asset/transfer/query-account-coins-balance"
    params = {"accountType": account_type}
    if coin:
        params["coin"] = coin.upper()

    body_str = ""  # GET の場合は空文字
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
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
    print(response.status_code, response.text)
