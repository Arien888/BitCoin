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
    message = timestamp + method.upper() + request_path + body
    print(f"[DEBUG] 署名対象メッセージ（長さ {len(message)}）:")
    print(f"  先頭100文字: {message[:100]}")
    print(f"  末尾100文字: {message[-100:]}")
    signature = base64.b64encode(
        hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    print(f"[DEBUG] 生成された署名(Base64): {signature}")
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
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }
    print(f"[DEBUG] 生成されたヘッダー: {headers}")
    print(f"[DEBUG] リクエストパス（署名対象）: {request_path}")

    return headers


def get_positions(key, secret, passphrase, sub_uid, base_path="/api/v2/mix/position/all-position"):
    method = "GET"
    # サブアカウントキーなら subUid パラメータは付けない
    query = ""  
    url = BASE_URL + base_path + query

    request_path_with_query = base_path + query
    headers = get_headers(key, secret, passphrase, method, request_path_with_query)

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

def close_position(key, secret, passphrase, sub_uid, symbol, position_side):
    method = "POST"
    request_path = "/api/v2/mix/order/close-position"
    url = BASE_URL + request_path

    body_dict = {
        "productType": "USDT-FUTURES",
        "symbol": symbol,
        "positionSide": position_side,
    }

    if sub_uid:
        body_dict["subUid"] = sub_uid

    body = json.dumps(body_dict)
    print(f"[DEBUG] close_position リクエストボディ: {body}")

    headers = get_headers(key, secret, passphrase, method, request_path, body)
    print(f"[DEBUG] close_position 署名ヘッダー: {headers}")

    try:
        response = requests.post(url, headers=headers, data=body)
    except Exception as e:
        print(f"[ERROR] close_position リクエスト失敗: {e}")
        return None

    print(f"[DEBUG] close_position ステータスコード: {response.status_code}")
    print(f"[DEBUG] close_position レスポンス: {response.text}")

    try:
        data = response.json()
        print(f"[DEBUG] close_position レスポンスJSON: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"[ERROR] close_position JSONパース失敗: {e}")
        return None

    if response.status_code == 200 and data.get("code") == "00000":
        print("ポジションをクローズしました。")
        return data
    else:
        print(f"APIエラーまたはHTTPエラー: {data}")
    return None


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
    base_path = "/api/v2/mix/position/all-position?productType=USDT-FUTURES"
    positions = get_positions(key, secret, passphrase, sub_uid, base_path=base_path)
    if not positions:
        print("[INFO] ポジションなし or 取得失敗")
        return

    # 取得したpositionsがリスト形式で各ポジション情報を含む想定
    for pos in positions:
        symbol = pos.get("symbol")
        position_side = pos.get("positionSide")  # long / short
        qty = float(pos.get("positionQty", 0))
        if qty == 0:
            continue

        print(f"[INFO] ポジションをクローズします: symbol={symbol}, side={position_side}, qty={qty}")
        res = close_position(key, secret, passphrase, sub_uid, symbol, position_side)
        if res:
            print(f"[INFO] クローズ成功: {symbol} {position_side}")
        else:
            print(f"[ERROR] クローズ失敗: {symbol} {position_side}")

if __name__ == "__main__":
    main()