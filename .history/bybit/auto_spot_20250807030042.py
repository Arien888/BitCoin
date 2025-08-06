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

url = "https://api.bybit.com/v5/order/create"

timestamp = str(int(time.time() * 1000))
# --- v5用のパラメータ ---
params = {
    "category": "spot",           # 現物取引
    "symbol": "BTCUSDT",
    "side": "Buy",
    "orderType": "Limit",         # または "Market"
    "qty": "0.001",
    "price": "116531.8",             # Market注文なら不要
    "timeInForce": "GTC",
    "timestamp": timestamp
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

# デバッグ出力
print("Status Code:", response.status_code)
print("Response Text:", response.text)

try:
    json_data = response.json()
    print(json_data)
except Exception as e:
    print("JSON decode error:", e)
