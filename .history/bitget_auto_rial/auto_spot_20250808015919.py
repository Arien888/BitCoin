import time
import hmac
import hashlib
import base64
import requests
import json
import xlwings as xw
import sys
import io
import os
import yaml
import xlwings as xw
from bitget_client import BitgetClient
from order_processor import place_orders  # bitget_orders → order_processor に変更
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# スクリプトのあるディレクトリ（どこから実行されても同じになる）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# config.yaml の読み込み
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Excel 関連設定
excel_rel_path = config["order_export"]["source_file"]
excel_path = excel_rel_path
buy_sheet = config["excel"]["sheets"]["buy"]

sheet_names = [
    config["excel"]["sheets"]["bitget_open_long_spot"],  # ロング用シート名
]

def get_timestamp():
    return str(int(time.time() * 1000))


def sign_bitget(api_secret, timestamp, method, request_path, body=""):
    message = f"{timestamp}{method.upper()}{request_path}{body}"
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def place_spot_order(symbol, side, order_type, qty, price=None, time_in_force="GTC"):
    api_key = config["bitget"]["api_key"]
    api_secret = config["bitget"]["secret"]
    passphrase = config["bitget"]["passphrase"]

    url = "https://api.bitget.com/api/spot/v1/trade/orders"
    request_path = "/api/spot/v1/trade/orders"
    method = "POST"
    timestamp = get_timestamp()

    try:
        qty = float(qty)
        if price is not None:
            price = float(price)
    except (ValueError, TypeError):
        print(f"[WARN] {symbol} → price={price}, qty={qty} → 数値化できずスキップ")
        return

    if price is not None and qty * price < 5:
        print(f"スキップ: {symbol} → {qty}×{price} = {qty * price}USDT（5未満）")
        return

    params = {
        "symbol": symbol,
        "side": side.lower(),  # buy/sell
        "orderType": order_type.upper(),  # LIMIT or MARKET
        "size": str(qty),
    }
    if order_type.upper() == "LIMIT" and price is not None:
        params["price"] = f"{price:.10f}".rstrip("0").rstrip(".")
    else:
        params.pop("price", None)

    body = json.dumps(params, separators=(",", ":"))

    sign = sign_bitget(api_secret, timestamp, method, request_path, body)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }

    print(f"=== 注文: {symbol} {side} {order_type} {qty} @ {price} ===")
    response = requests.post(url, headers=headers, data=body)
    print("レスポンス:", response.text)
    return response.json()


def read_orders_from_excel(sheet_name):
    excel_path = config["order_export"]["source_file"]

    app = xw.App(visible=False)
    app.calculation = "automatic"
    app.display_alerts = False

    try:
        wb = app.books.open(excel_path)
        time.sleep(10)
        sheet = wb.sheets[sheet_name]
        orders = []

        for row in range(2, 101):
            symbol = sheet.range(f"A{row}").value
            side = sheet.range(f"B{row}").value
            order_type = sheet.range(f"C{row}").value
            qty = sheet.range(f"D{row}").value
            price = sheet.range(f"E{row}").value

            if not symbol or not side or not order_type or not qty:
                continue

            orders.append(
                {
                    "symbol": symbol,
                    "side": side,
                    "order_type": order_type,
                    "qty": qty,
                    "price": price if price != "" else None,
                }
            )

        return orders

    finally:
        wb.close()
        app.quit()


if __name__ == "__main__":
    for sheet_name in sheet_names:
        print(f"=== {sheet_name} シートの注文を処理 ===")
        orders = read_orders_from_excel(sheet_name)
        for order in orders:
            result = place_spot_order(
                order["symbol"],
                order["side"],
                order["order_type"],
                order["qty"],
                order["price"],
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
