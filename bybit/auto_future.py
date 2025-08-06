import time
import hmac
import hashlib
import requests
import json
import os
import openpyxl
from load_config import load_config

config = load_config()

sheet_names = [
    config["excel"]["sheets"]["open_long_big_margin"],  # ロング用シート名
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def place_order(symbol, side, order_type, qty, price=None, time_in_force="GTC"):
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    url = "https://api.bybit.com/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    try:
        price =float(price)
        qty =float(qty)
    except (ValueError, TypeError):
        print(f"[WARN] {symbol} の価格または数量が数値に変換できません。値: price={price}, quantity={qty} → スキップします。")

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
    signature = hmac.new(
        api_secret.encode(), origin_string.encode(), hashlib.sha256
    ).hexdigest()

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


import xlwings as xw
import time

def read_orders_from_excel(sheet_name):
    excel_rel_path = config["order_export"]["source_file"]
    excel_path = excel_rel_path

    app = xw.App(visible=False)
    app.calculation = "automatic"  # 念のため計算モード
    app.display_alerts = False

    try:
        wb = app.books.open(excel_path)
        time.sleep(10)

        sheet = wb.sheets[sheet_name]
        orders = []

        # 2行目から100行目まで読む（必要に応じて調整）
        for row in range(2, 101):
            symbol = sheet.range(f"A{row}").value
            side = sheet.range(f"B{row}").value
            order_type = sheet.range(f"C{row}").value
            qty = sheet.range(f"D{row}").value
            price = sheet.range(f"E{row}").value

            if not symbol or not side or not order_type or not qty:
                continue

            orders.append({
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "qty": qty,
                "price": price if price != "" else None,
            })

        return orders

    finally:
        wb.close()
        app.quit()


if __name__ == "__main__":
    for sheet_name in sheet_names:
        print(f"=== {sheet_name} シートの注文を処理 ===")
        orders = read_orders_from_excel(sheet_name)
        for order in orders:
            result = place_order(
                order["symbol"],
                order["side"],
                order["order_type"],
                order["qty"],
                order["price"],
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
