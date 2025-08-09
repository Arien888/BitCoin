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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_URL = "https://api.bitget.com"

def mask_str(s, head=4, tail=4):
    if len(s) <= head + tail:
        return "*" * len(s)
    return s[:head] + "*" * (len(s) - head - tail) + s[-tail:]

def get_passphrase_signature(secret, passphrase):
    mac = hmac.new(secret.encode(), passphrase.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

def create_signature(secret, method, request_path, timestamp, body=""):
    # bodyは空文字列かJSON文字列のはず
    message = timestamp + method.upper() + request_path + body
    print(f"[DEBUG] 署名対象メッセージ（長さ {len(message)}）:")
    # 長すぎると見づらいので先頭・末尾を分けて表示してもいい
    print(f"  先頭100文字: {message[:100]}")
    print(f"  末尾100文字: {message[-100:]}")
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    print(f"[DEBUG] 生成された署名: {signature}")
    return signature


def get_headers(key, secret, passphrase, method, request_path, body=""):
    timestamp = str(int(time.time() * 1000))
    print(f"[DEBUG] タイムスタンプ: {timestamp}")
    sign = create_signature(secret, method, request_path, timestamp, body)
    passphrase_signature = get_passphrase_signature(secret, passphrase)
    print(f"[DEBUG] パスフレーズ署名: {passphrase_signature}")

    headers = {
        "ACCESS-KEY": key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase_signature,
        "Content-Type": "application/json",
    }
    print(f"[DEBUG] 生成されたヘッダー: {headers}")
    print(f"[DEBUG] リクエストパス（署名対象）: {request_path}")

    return headers

def get_positions(key, secret, passphrase, sub_uid, base_path="/api/v2/mix/position/all-position"):
    method = "GET"
    query = f"?subUid={sub_uid}" if sub_uid else ""
    url = BASE_URL + base_path + query

    print(f"[DEBUG] 使用APIエンドポイントパス: {base_path}")
    print(f"[DEBUG] リクエストURL: {url}")
    print(f"[DEBUG] APIキー (mask): {mask_str(key)}")
    print(f"[DEBUG] APIシークレット (mask): {mask_str(secret)}")
    print(f"[DEBUG] パスフレーズ: {passphrase}")
    print(f"[DEBUG] サブアカウントID: {sub_uid}")

    headers = get_headers(key, secret, passphrase, method, base_path)

    res = requests.get(url, headers=headers)

    print(f"[DEBUG] レスポンスステータスコード: {res.status_code}")
    print(f"[DEBUG] レスポンス内容: {res.text}")

    if res.status_code != 200:
        print(f"[ERROR] ポジション取得失敗: {res.text}")
        return None
    data = res.json()
    if data.get("code") != "00000":
        print(f"[ERROR] ポジション取得エラー: {data}")
        return None
    return data["data"]

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    key = config["bitget"]["subaccount"]["api_key"]
    secret = config["bitget"]["subaccount"]["api_secret"]
    passphrase = config["bitget"]["subaccount"]["passphrase"]
    sub_uid = config["bitget"]["subaccount"].get("sub_uid", "")

    print(f"[DEBUG] 全設定読み込み完了")
    print(f"[DEBUG] APIキー: {mask_str(key)}")
    print(f"[DEBUG] APIシークレット: {mask_str(secret)}")
    print(f"[DEBUG] パスフレーズ: {passphrase}")
    print(f"[DEBUG] サブアカウントUID: {sub_uid}")

    print("[INFO] サブアカウント先物ポジションを取得します...")
    # APIタイプは設定や用途により変更
    base_path = "/api/v2/mix/position/all-position"  # mixタイプAPI
    positions = get_positions(key, secret, passphrase, sub_uid, base_path=base_path)
    if not positions:
        print("[INFO] ポジションなし or 取得失敗")
        return

    # 以降の処理...

if __name__ == "__main__":
    main()
