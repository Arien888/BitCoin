import sys
import io
import os
import yaml
import time
import requests
import hmac
import hashlib

# --- 出力をUTF-8に設定 ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# --- スクリプトのあるディレクトリ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- config.yaml 読み込み ---
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

API_KEY = config["bitget"]["api_key"]
API_SECRET = config["bitget"]["api_secret"]
PASSPHRASE = config["bitget"]["passphrase"]
IS_TESTNET = config["bitget"].get("is_testnet", False)

BASE_URL = "https://api.bitget.com" if not IS_TESTNET else "https://api-testnet.bitget.com"

# --- Bitget API署名生成 ---
def sign_request(method, request_path, body=""):
    timestamp = str(int(time.time() * 1000))
    pre_sign = f"{timestamp}{method}{request_path}{body}"
    sign = hmac.new(API_SECRET.encode("utf-8"), pre_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    return timestamp, sign

# --- 資金振替 ---
def transfer_funds(from_type, to_type, coin, amount, client_oid=None):
    path = "/api/v2/spot/wallet/transfer"
    url = BASE_URL + path

    body = {
        "fromType": from_type,      # "spot"
        "toType": to_type,          # "usdt_futures"
        "coin": coin,               # "USDT"
        "amount": str(amount),      # 数値は文字列で送る
        "clientOid": client_oid or str(int(time.time() * 1000))
    }

    import json
    body_str = json.dumps(body, separators=(",", ":"))

    timestamp, sign = sign_request("POST", path, body_str)

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    r = requests.post(url, headers=headers, data=body_str)
    return r.json()

# --- メイン処理 ---
def main():
    try:
        print("[INFO] 資金振替を開始します...")

        # 例: Spot → USDT先物に 100 USDT を送金
        result = transfer_funds("spot", "usdt_futures", "USDT", 100)

        print("[INFO] 振替結果:")
        print(result)

    except Exception as e:
        import traceback
        print(f"[ERROR] 処理中に例外が発生しました: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
