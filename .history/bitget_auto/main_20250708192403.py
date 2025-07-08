import sys
import io
import os
import yaml
import xlwings as xw
from bitget_client import BitgetClient

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

excel_path = config["excel"]["path"]
buy_sheet = config["excel"]["sheets"]["buy"]
sell_sheet = config["excel"]["sheets"]["sell"]

client = BitgetClient(
    key=config["bitget"]["api_key"],
    secret=config["bitget"]["api_secret"],
    passphrase=config["bitget"]["passphrase"],
)

MIN_ORDER_AMOUNT_USDT = 5


def is_valid_order(price, quantity):
    if quantity is None or quantity <= 0:
        print(f"[WARN] quantityが0以下のためスキップします: quantity={quantity}")
        return False
    if price * quantity < MIN_ORDER_AMOUNT_USDT:
        print(f"[WARN] 注文額が最低注文額未満のためスキップします: price={price} quantity={quantity} 合計={price*quantity}")
        return False
    return True


def read_orders_from_sheet(wb, sheet_name):
    if sheet_name not in [s.name for s in wb.sheets]:
        print(f"[ERROR] シートが存在しません: {sheet_name}")
        return []

    sheet = wb.sheets[sheet_name]
    orders = []

    for row in range(2, sheet.api.UsedRange.Rows.Count + 1):
        symbol = sheet.range(f"A{row}").value
        side = sheet.range(f"B{row}").value
        price = sheet.range(f"C{row}").value
        quantity = sheet.range(f"D{row}").value
        order_type = sheet.range(f"E{row}").value

        if not symbol:
            continue

        print(f"[DEBUG] Excel読み込み行{row}: {symbol}, {side}, {price}, {quantity}, {order_type}")
        orders.append((symbol, side, price, quantity, order_type))

    return orders


def main():
    print("[INFO] Excelファイルを開きます...")
    app = xw.App(visible=False)
    wb = None

    try:
        wb = app.books.open(excel_path)

        print("[INFO] Buyシートから読み込み:")
        buy_orders = read_orders_from_sheet(wb, buy_sheet)
        for order in buy_orders:
            symbol, side, price, quantity, order_type = order
            if not is_valid_order(price, quantity):
                continue
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(*order)

        print("[INFO] Sellシートから読み込み:")
        sell_orders = read_orders_from_sheet(wb, sell_sheet)
        for order in sell_orders:
            symbol, side, price, quantity, order_type = order
            if not is_valid_order(price, quantity):
                continue
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(*order)

    except Exception as e:
        print(f"[ERROR] 処理中に例外が発生しました: {e}")

    finally:
        if wb:
            try:
                wb.close()
            except Exception as e:
                print(f"[WARN] Excelファイルを閉じるときに失敗: {e}")
        app.quit()


if __name__ == "__main__":
    main()
