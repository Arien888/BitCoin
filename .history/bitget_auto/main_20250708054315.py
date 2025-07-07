import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urljoin
import openpyxl

# --- API情報 ---
key  = "あなたのAPIキー"
secret  = "あなたのシークレット"
API_PASSPHRASE = "あなたのパスフレーズ"
BASE_URL = "https://api.bitget.com"

# --- シグネチャ生成 ---
def generate_signature(timestamp, method, request_path, body):
    message = f"{timestamp}{method}{request_path}{body}"
    hmac_key = hmac.new(secret .encode(), message.encode(), hashlib.sha256)
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
        "externalOid": ""
    }
    body = json.dumps(body_dict)

    signature = generate_signature(timestamp, "POST", path, body)
    headers = {
        "Content-Type": "application/json",
        "ACCESS-KEY": key ,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
    }

    print(f"▶️ 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
    try:
        res = requests.post(url, headers=headers, data=body, timeout=15)
        res.raise_for_status()
        data = res.json()
        print("← レスポンス:", json.dumps(data, indent=2, ensure_ascii=False))
        return data
    except Exception as e:
        print("❌ 発注エラー:", e)
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
    print("📋 Excel注文データ一覧:")
    for order in orders:
        print(order)
        place_order(*order)

if __name__ == "__main__":
    main()
