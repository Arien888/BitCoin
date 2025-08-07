import time
import hashlib
import hmac
import requests
import json

# APIキーとシークレット
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

url = "https://api.bybit.com/spot/v3/private/order"

timestamp = str(int(time.time() * 1000))

params = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "price": "65000",
    "qty": "0.001",
    "timeInForce": "GTC",
    "timestamp": timestamp,
    "recvWindow": 5000
}

# パラメータの順序を保証して文字列化
param_str = "&".join([f"{key}={params[key]}" for key in sorted(params)])
signature = hmac.new(
    api_secret.encode("utf-8"),
    param_str.encode("utf-8"),
    hashlib.sha256
).hexdigest()

headers = {
    "X-BYBIT-API-KEY": api_key,
    "Content-Type": "application/json"
}

params["sign"] = signature

response = requests.post(url, headers=headers, data=json.dumps(params))
print(response.json())
