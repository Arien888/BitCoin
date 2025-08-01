import time
import hmac
import hashlib
import requests
import json
import os
import openpyxl
from load_config import load_config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def place_order(symbol, side, order_type, qty, price=None, time_in_force="GTC"):
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    url = "https://api.bybit.com/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    # 注文金額チェック（5USDT未満は発注しない）
    if price is not None and float(qty) * float(price) < 5:
        print(f"スキップ: {symbol} → {qty}×{price} = {qty * price}USDT（5未満）")
        return

    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "qty": str(qty),
        "timeInForce": time_in_force,
    }
    if order_type == "Limit" and price is not None:
        body["price"] = f"{price:.10f}".rstrip("0").rstrip(".")

    body_str = json.dumps(body)
    origin_string = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(api_secret.encode(), origin_string.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))

    print(f"=== 注文: {symbol} {side} {order_type} {qty} @ {price} ===")
    print("レスポンス:", response.text)
    return response.json()


def read_orders_from_excel():
    config = load_config()
    excel_rel_path = config["excel"]["path"]
    sheet_name = config["excel"]["big_margin"]["open_long"]
    excel_path = os.path.join(BASE_DIR, "..", excel_rel_path)

    wb = openpyxl.load_workbook(excel_path)
    sheet = wb[sheet_name]

    orders = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        symbol, side, order_type, qty, price = row
        if not symbol or not side or not order_type or not qty:
            continue
        orders.append({
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "qty": qty,
            "price": price if price != "" else None
        })
    return orders


if __name__ == "__main__":
    orders = read_orders_from_excel()
    for order in orders:
        result = place_order(
            order["symbol"],
            order["side"],
            order["order_type"],
            order["qty"],
            order["price"]
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
