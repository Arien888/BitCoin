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
api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

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

# --- 署名作成 ---
# パラメータを文字列化（キー順に並べて）
param_str = "&".join(f"{k}={params[k]}" for k in sorted(params))
signature = hmac.new(
    api_secret.encode("utf-8"),
    param_str.encode("utf-8"),
    hashlib.sha256
).hexdigest()

# --- ヘッダー設定 ---
headers = {
    "X-BYBIT-API-KEY": api_key,
    "X-BYBIT-SIGN": signature,
    "X-BYBIT-TIMESTAMP": timestamp,
    "Content-Type": "application/json"
}

# --- API送信 ---
response = requests.post(url, headers=headers, json=params)

# --- デバッグ出力 ---
print("Status Code:", response.status_code)
print("Response:", response.text)