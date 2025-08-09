import requests
import time
import hmac
import hashlib
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# スクリプトのあるディレクトリ（どこから実行されても同じになる）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# config.yaml の読み込み
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

BASE_URL = "https://api.bitget.com"


# --- 認証ヘッダー作成 ---
def create_signature(api_secret, method, request_path, timestamp, body=""):
    message = timestamp + method + request_path + body
    signature = hmac.new(
        api_secret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return signature


def get_headers(api_key, api_secret, api_passphrase, method, request_path, body=""):
    timestamp = str(int(time.time() * 1000))
    sign = create_signature(api_secret, method, request_path, timestamp, body)
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": api_passphrase,
        "Content-Type": "application/json",
    }
    return headers


# --- サブアカウントの先物ポジションを取得 ---
def get_positions(api_key, api_secret, api_passphrase, sub_uid):
    path = f"/api/futures/v3/position/singlePosition?subUid={sub_uid}"
    method = "GET"
    url = BASE_URL + path
    headers = get_headers(api_key, api_secret, api_passphrase, method, path)
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"[ERROR] ポジション取得失敗: {res.text}")
        return None
    data = res.json()
    if data.get("code") != "00000":
        print(f"[ERROR] ポジション取得エラー: {data}")
        return None
    return data["data"]


# --- ポジションクローズ（成行注文） ---
def close_position(api_key, api_secret, api_passphrase, sub_uid, symbol, side, size):
    # sideは「buy」か「sell」。ポジションがロングなら売り注文でクローズ、ショートなら買い注文でクローズ。
    path = "/api/futures/v3/order"
    method = "POST"

    # ポジションを閉じる注文パラメータ
    body = {
        "symbol": symbol,
        "size": str(size),
        "side": side,
        "type": "market",
        "open_type": "close",  # ポジションクローズ指定
        "leverage": "10",  # 適宜変更
        "external_oid": f"close_{int(time.time()*1000)}",
        "sub_uid": sub_uid,
    }
    body_json = json.dumps(body)
    url = BASE_URL + path
    headers = get_headers(api_key, api_secret, api_passphrase, method, path, body_json)
    res = requests.post(url, headers=headers, data=body_json)
    if res.status_code == 200:
        resp = res.json()
        if resp.get("code") == "00000":
            print(f"[INFO] {symbol}の{side}成行クローズ注文成功: {resp['data']}")
            return True
        else:
            print(f"[ERROR] 注文エラー: {resp}")
            return False
    else:
        print(f"[ERROR] HTTPエラー: {res.status_code} {res.text}")
        return False


def main():
    # 設定ファイルから読み込み
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    api_key = config["subaccount"]["bitget_Unified"]["api_key"]
    api_secret = config["subaccount"]["bitget_Unified"]["secret_key"]
    api_passphrase = config["subaccount"]["bitget_Unified"]["passphrase"]
    sub_uid = config["subaccount"]["bitget_Unified"]["sub_uid"]

    print("[INFO] サブアカウント先物ポジションを取得します...")
    positions = get_positions(api_key, api_secret, api_passphrase, sub_uid)
    if not positions:
        print("[INFO] ポジションなし or 取得失敗")
        return

    # positionsはポジションのリスト。symbolごとにロングとショートのサイズがある想定
    for pos in positions:
        symbol = pos["symbol"]
        long_size = float(pos.get("long_qty", 0))
        short_size = float(pos.get("short_qty", 0))

        if long_size > 0:
            print(f"[INFO] {symbol} ロング {long_size} を売り成行でクローズします...")
            close_position(
                api_key, api_secret, api_passphrase, sub_uid, symbol, "sell", long_size
            )
        if short_size > 0:
            print(
                f"[INFO] {symbol} ショート {short_size} を買い成行でクローズします..."
            )
            close_position(
                api_key, api_secret, api_passphrase, sub_uid, symbol, "buy", short_size
            )

    print("[INFO] 全ポジションクローズ処理完了")


if __name__ == "__main__":
    main()
