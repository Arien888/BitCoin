import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urljoin
import openpyxl

# --- API情報 ---
key = "あなたのAPIキー"
secret = "あなたのシークレット"
passphrase = "あなたのパスフレーズ"
BASE_URL = "https://api.bitget.com"


# --- シグネチャ生成 ---
def generate_signature(timestamp, method, request_path, body):
    message = f"{timestamp}{method}{request_path}{body}"
    hmac_key = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
    return hmac_key.hexdigest()


# --- 注文送信 ---
def place_order(symbol, side, price, quantity, order_type):
    path = "/api/mix/v1/order/placeOrder"
    url = urljoin(BASE_URL, path)

    timestamp = str(int(time.time() * 1000))
    body_dict = {
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
    print(info_msg.encode("ascii", "ignore").decode())
    try:
        res = requests.post(url, headers=headers, data=body, timeout=15)
        res.raise_for_status()
        data = res.json()
        print(
            "API応答を受信（内容はUTF-8ログに記録）".encode("ascii", "ignore").decode()
        )

        with open("bitget_response_log.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n\n")

        return data

    except Exception as e:
        safe_error = str(e).encode("ascii", "ignore").decode()
        print("[ERROR]", safe_error)

        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(str(e) + "\n")

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
    print("[INFO] Excel注文データ一覧:")
    for order in orders:
        print(order)
        place_order(*order)


if __name__ == "__main__":
    main()
