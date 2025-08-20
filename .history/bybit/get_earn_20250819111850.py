import time
import hmac
import hashlib
import requests

api_key = "your_api_key"
api_secret = "your_api_secret"

url = "https://api.bybit.com/v5/asset/transfer/query-account-coins-balance"
params = {"accountType": "SPOT"}

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

# ← ここで必ず出力する
print("Status Code:", response.status_code)
print("Response Body:", response.text)
