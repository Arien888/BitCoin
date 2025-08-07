import time
import hmac
import hashlib
import requests
import json
import xlwings as xw
from load_config import load_config  # config読み込みは同様に
config = load_config()

sheet_names = [
    config["excel"]["sheets"]["bybit_open_long_chash"],  # ロング用シート名
]


def place_spot_order(symbol, side, order_type, qty, price=None, time_in_force="GTC"):
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    url = "https://api.bybit.com/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    try:
        qty = float(qty)
        if price is not None:
            price = float(price)
    except (ValueError, TypeError):
        print(
            f"[WARN] {symbol} の価格または数量が数値に変換できません。price={price}, qty={qty} → スキップします。"
        )
        return

    # 注文金額が5USDT未満なら発注しない
    if price is not None and qty * price < 5:
        print(f"スキップ: {symbol} → {qty}×{price} = {qty * price}USDT（5未満）")
        return

    body = {
        "category": "spot",  # 現物は "spot"
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "qty": str(qty),
        "timeInForce": time_in_force,
    }
    if order_type == "Limit" and price is not None:
        # 余計な0は落とす（先物の書き方に合わせる）
        body["price"] = f"{price:.10f}".rstrip("0").rstrip(".")

    body_str = json.dumps(body, separators=(",", ":"))  # コンパクトに

    # 署名用文字列作成
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

    # 送信は data=body_str に注意
    response = requests.post(url, headers=headers, data=body_str)

    print(f"=== 注文: {symbol} {side} {order_type} {qty} @ {price} ===")
    print("レスポンス:", response.text)
    return response.json()


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
