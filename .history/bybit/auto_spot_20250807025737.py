import time
import hashlib
import hmac
import requests
import json
import yaml
from pathlib import Path
# 一つ上の階層のconfig.yamlのパスを取得
config_path = Path(__file__).resolve().parent.parent / "config.yaml"

# YAMLファイルの読み込み
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# APIキーとシークレットの取得
key = config["bybit"]["key"]
secret = config["bybit"]["secret"]

url = "https://api.bybit.com/spot/v3/private/order"

timestamp = str(int(time.time() * 1000))

params = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "price": "116531.8",
    "qty": "0.001",
    "timeInForce": "GTC",
    "timestamp": timestamp,
    "recvWindow": 5000
}

# パラメータの順序を保証して文字列化
param_str = "&".join([f"{key}={params[key]}" for key in sorted(params)])
signature = hmac.new(
    secret.encode("utf-8"),
    param_str.encode("utf-8"),
    hashlib.sha256
).hexdigest()

headers = {
    "X-BYBIT-API-KEY": key,
    "Content-Type": "application/json"
}

params["sign"] = signature

response = requests.post(url, headers=headers, data=json.dumps(params))
print(response.json())
