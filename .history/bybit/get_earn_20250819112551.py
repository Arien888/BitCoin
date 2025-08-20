import time
import hmac
import hashlib
import requests
import json
from load_config import load_config

# --- 設定読み込み ---
config = load_config()
api_key = config["bybit"]["key"]
api_secret = config["bybit"]["secret"]

def get_earn_balance():
    # 最新のV5 Earn残高取得エンドポイント
    url = "https://api.bybit.com/v5/earn/account"  # On-Chain Earn用
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    body_str = ""  # GETなら空文字列

    # --- 署名作成 ---
    origin_string = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(
        api_secret.encode(),
        origin_string.encode(),
        hashlib.sha256
    ).hexdigest()

    # --- ヘッダー ---
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }

    # --- デバッグ情報 ---
    print("=== DEBUG ===")
    print("Request URL:", url)
    print("Request Headers:", headers)
    print("Origin String for Signature:", origin_string)
    print("Signature:", signature)
    print("Body:", body_str)
    print("=== END DEBUG ===\n")

    try:
        response = requests.get(url, headers=headers)
        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Body:", response.text)
        response.raise_for_status()
        data = response.json()
        if data.get("retCode") != 0:
            print("[ERROR] API returned error:", data.get("retMsg"))
            return None
        return data.get("result", {}).get("list", [])
    except requests.exceptions.HTTPError as e:
        print("[HTTP ERROR]", e)
    except requests.exceptions.RequestException as e:
        print("[REQUEST EXCEPTION]", e)
    except json.JSONDecodeError as e:
        print("[JSON ERROR]", e, "\nResponse Text:", response.text)
    return None

if __name__ == "__main__":
    balances = get_earn_balance()
    if balances:
        print("\n=== Earn Balances ===")
        for b in balances:
            print(json.dumps(b, indent=2, ensure_ascii=False))
    else:
        print("\nNo balances retrieved or error occurred.")
