import os
import yaml
import ccxt

# --- 設定ファイルの読み込み ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["bitbank"]["api_key"]
secret = config["bitbank"]["api_secret"]

# --- Bitbank クライアント作成 ---
bitbank = ccxt.bitbank({
    "apiKey": api_key,
    "secret": secret,
})

# --- 残高取得 ---
try:
    balance = bitbank.fetch_balance()
except Exception as e:
    print("残高取得エラー:", e)
    balance = {}

# --- 有効残高を表示 ---
if balance:
    print("保有銘柄と数量:")
    # balance['total'] に各通貨の総保有量が入っている
    for asset, amount in balance.get('total', {}).items():
        if amount and amount > 0:
            print(f"{asset}: {amount}")
