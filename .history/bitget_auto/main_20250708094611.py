import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urljoin
import openpyxl
import sys
import io
import os
import yaml
import base64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
# 親ディレクトリのconfig.yamlのパス
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

# config.yamlを読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

excel_path = config["excel"]["path"]

# API情報を取得
key = config["bitget"]["api_key"]
secret = config["bitget"]["api_secret"]
passphrase = config["bitget"]["passphrase"]
BASE_URL = "https://api.bitget.com"


# --- シグネチャ生成 ---
def generate_signature(timestamp, method, request_path, body):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


# --- 注文送信 ---
def place_order(symbol, side, price, quantity, order_type):
    # Excelの "buy" / "sell" を Bitget用に変換
    side_map = {"buy": "open_long", "sell": "open_short"}
    side = side_map.get(side.lower(), side)  # 万一未定義でも元の文字列を残す
    path = "/api/mix/v1/order/placeOrder"
    url = urljoin(BASE_URL, path)

    timestamp = str(int(time.time() * 1000))

    body_dict = {
        "marginCoin": "USDT",
        "productType": "UMCBL",  # ← これが必要！
        "symbol": symbol,
        "side": side.upper(),  # BUY or SELL
        "orderType": order_type.upper(),  # LIMIT or MARKET
        "price": str(price) if order_type.lower() == "limit" else "",
        "size": str(quantity),
        "timeInForce": "GTC",
        "reduceOnly": False,
        "closeOrder": False,
        "positionId": 0,
        "visibleSize": "0",
        "externalOid": "",
    }
    body = json.dumps(body_dict)

    signature = generate_signature(timestamp, "POST", path, body)
    headers = {
        "Content-Type": "application/json",
        "ACCESS-KEY": key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
    }

    info_msg = f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}"

    # ここに追加
    print(info_msg)
    # print(info_msg.encode("utf-8"))
    # print(info_msg.encode("ascii", "ignore").decode())
    try:
        res = requests.post(url, headers=headers, data=body, timeout=15)
        print("[DEBUG] ステータスコード:", res.status_code)  # ← 追加
        print("[DEBUG] レスポンステキスト:", res.text)  # ← 追加
        res.raise_for_status()
        data = res.json()
        print(
            "API応答を受信（内容はUTF-8ログに記録）".encode("ascii", "ignore").decode()
        )
        print(json.dumps(data, indent=2, ensure_ascii=False))  # ← ここ追加

        with open("bitget_response_log.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n\n")

        return data

    except Exception as e:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(str(e) + "\n")
            # コンソールにはエラーメッセージを出さない or 簡単な英数字だけにする

            return None


# --- Excelから読み込み ---
def read_orders_from_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    orders = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        symbol, side, price, quantity, order_type = row
        orders.append((symbol, side, price, quantity, order_type))
    return orders


# --- メイン ---
def main():
    orders = read_orders_from_excel("orders.xlsx")
    print("[INFO] Excel注文データ一覧:".encode("ascii", "ignore").decode())

    for order in orders:
        safe_order = tuple(str(x).encode("ascii", "ignore").decode() for x in order)
        print(safe_order)
        place_order(*order)


if __name__ == "__main__":
    main()
