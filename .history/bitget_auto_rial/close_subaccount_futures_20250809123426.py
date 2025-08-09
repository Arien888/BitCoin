import requests
import time
import hmac
import hashlib
import json
import sys
import io
import os
import yaml
import base64
import hmac
import hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


BASE_URL = "https://api.bitget.com"


# --- 認証ヘッダー作成 ---
def create_signature(secret, method, request_path, timestamp, body=""):
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
    signature = base64.b64encode(mac.digest()).decode()
    return signature


def get_headers(key, secret, passphrase, method, request_path, body=""):
    timestamp = str(int(time.time() * 1000))
    sign = create_signature(secret, method, request_path, timestamp, body)
    headers = {
        "ACCESS-KEY": key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }
    return headers


def get_positions(key, secret, passphrase, sub_uid):
    path = f"/api/v2/mix/position/all-position?subUid={sub_uid}"  # ←ここを修正
    method = "GET"
    url = BASE_URL + path
    headers = get_headers(key, secret, passphrase, method, path, "")  # bodyは空文字
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
def close_position(key, secret, passphrase, sub_uid, symbol, side, size):
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
    headers = get_headers(key, secret, passphrase, method, path, body_json)
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
    # スクリプトのあるディレクトリ（どこから実行されても同じになる）
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 設定ファイルから読み込み
    # config.yaml の読み込み
    with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    key = config["bitget"]["subaccount"]["api_key"]
    secret = config["bitget"]["subaccount"]["api_secret"]
    passphrase = config["bitget"]["subaccount"]["passphrase"]
    is_testnet = config["bitget"]["subaccount"].get(
        "is_testnet", False
    )  # ← ここで切り替え

    print("[INFO] サブアカウント先物ポジションを取得します...")
    positions = get_positions(key, secret, passphrase, is_testnet)
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
                key, secret, passphrase, is_testnet, symbol, "sell", long_size
            )
        if short_size > 0:
            print(
                f"[INFO] {symbol} ショート {short_size} を買い成行でクローズします..."
            )
            close_position(
                key, secret, passphrase, is_testnet, symbol, "buy", short_size
            )

    print("[INFO] 全ポジションクローズ処理完了")


if __name__ == "__main__":
    main()
