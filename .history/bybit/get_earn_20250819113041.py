import time
import hmac
import hashlib
import requests
from load_config import load_config

config = load_config()
api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

timestamp = str(int(time.time() * 1000))
recv_window = "5000"
account_type = "SPOT"  # SPOT, CONTRACT, MARGINなど

# 署名用に URL クエリも含める
query_string = f"accountType={account_type}"
origin_string = f"{timestamp}{api_key}{recv_window}{query_string}"
signature = hmac.new(api_secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()

url = f"https://api.bybit.com/v5/account/wallet-balance?{query_string}"

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
