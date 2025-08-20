import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urlencode
from load_config import load_config

config = load_config()

# === 共通: 署名作成 ===
def _sign_and_headers(query_or_body_str: str):
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    origin_string = f"{timestamp}{api_key}{recv_window}{query_or_body_str}"
    signature = hmac.new(api_secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }
    return headers

# === Bybit Earn資産を取得 ===
def get_bybit_earn_balances(coin: str | None = None, with_bonus: int = 0):
    """
    Bybit v5: Get All Coins Balance
    GET /v5/asset/transfer/query-account-coins-balance?accountType=INVESTMENT
    """
    base_url = "https://api.bybit.com"
    path = "/v5/asset/transfer/query-account-coins-balance"
    params = {"accountType": "INVESTMENT"}
    if coin:
        params["coin"] = coin.upper()
    if with_bonus in (0, 1):
        params["withBonus"] = str(with_bonus)

    query_str = urlencode(params, doseq=True)
    headers = _sign_and_headers(query_str)
    url = f"{base_url}{path}?{query_str}"

    r = requests.get(url, headers=headers)
    data = r.json()

    if data.get("retCode") != 0:
        raise RuntimeError(f"Earn残高取得失敗: {data.get('retCode')} {data.get('retMsg')}")

    return data.get("result", {}).get("list", [])

if __name__ == "__main__":
    try:
        balances = get_bybit_earn_balances()
        print("=== Bybit Earn (INVESTMENT) 残高 ===")
        print(json.dumps(balances, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[ERROR] Earn残高取得に失敗: {e}")
