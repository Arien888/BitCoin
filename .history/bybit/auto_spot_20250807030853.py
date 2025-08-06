import time
import hashlib
import hmac
import requests
import json
import yaml
from pathlib import Path

# --- 設定ファイルの読み込み ---
config_path = Path(__file__).resolve().parent.parent / "config.yaml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

# --- Bybit API v5 エンドポイント ---
url = "https://api.bybit.com/v5/order/create"
timestamp = str(int(time.time() * 1000))
recv_window = "5000"  # 任意（署名には含める）

# --- 注文パラメータ ---
params = {
    "category": "spot",
    "symbol": "BTCUSDT",
    "side": "Buy",
    "orderType": "Limit",
    "qty": "0.001",
    "price": "116531.8",
    "timeInForce": "GTC"
}

# --- 署名対象文字列の構築 ---
body_str = json.dumps(params, separators=(",", ":"), ensure_ascii=False)
signing_string = timestamp + api_key + recv_window + body_str

signature = hmac.new(
    api_secret.encode("utf-8"),
    signing_string.encode("utf-8"),
    hashlib.sha256
).hexdigest()

# ヘッダーに署名等設定（これは問題なし）
headers = {
    "X-BYBIT-API-KEY": api_key,
    "X-BYBIT-SIGN": signature,
    "X-BYBIT-TIMESTAMP": timestamp,
    "X-BYBIT-RECV-WINDOW": recv_window,
    "Content-Type": "application/json"
}
print("Headers being sent:")
for k, v in headers.items():
    print(f"{k}: {v}")


print(f"URL: {url}")
print(f"Timestamp: {timestamp}")
print(f"Signature: {signature}")
print(f"API key: {api_key}")
print(f"Headers: {headers}")
print(f"Body: {body_str}")


# ここを json=params ではなく data=body_str にすること
response = requests.post(url, headers=headers, data=body_str)
# --- デバッグ出力 ---
print("Status Code:", response.status_code)
print("Response:", response.text)

