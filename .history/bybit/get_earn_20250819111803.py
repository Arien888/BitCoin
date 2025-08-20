import time
import hmac
import hashlib
import requests

def get_earn_balance(api_key, api_secret, account_type="SPOT", coin=None):
    url = "https://api.bybit.com/v5/asset/transfer/query-account-coins-balance"
    params = {
        "accountType": account_type,
        "coin": coin.upper() if coin else None
    }
    params = {k: v for k, v in params.items() if v is not None}  # None を除外

    # タイムスタンプと署名の生成
    timestamp = str(int(time.time() * 1000))
    query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    sign_payload = f"{timestamp}{api_key}{query_string}"
    signature = hmac.new(api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("retCode") == 0:
            return data.get("result", {}).get("list", [])
        else:
            print(f"Error: {data.get('retMsg')}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None

# 使用例
api_key = "your_api_key"
api_secret = "your_api_secret"
balances = get_earn_balance(api_key, api_secret, coin="USDT")
if balances:
    for balance in balances:
        print(balance)
