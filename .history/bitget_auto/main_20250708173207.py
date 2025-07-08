import sys
import io
import os
import yaml
import xlwings as xw
from bitget_client import BitgetClient

# 標準出力の文字化け対策（Windows）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 設定ファイルのパス
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

# 設定の読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

excel_path = config["excel"]["path"]
buy_sheet = config["excel"]["sheets"]["buy"]
sell_sheet = config["excel"]["sheets"]["sell"]

# Bitgetクライアント初期化
client = BitgetClient(
    key=config["bitget"]["api_key"],
    secret=config["bitget"]["api_secret"],
    passphrase=config["bitget"]["passphrase"],
)


def read_orders_from_excel(book, sheet_name):
    sheet = book.sheets[sheet_name]

    orders = []
    row = 2
    while True:
        values = sheet.range(f"A{row}:E{row}").value
        if not values or not values[0]:
            break  # A列が空なら終了
        orders.append(tuple(values))
        row += 1
    return orders


MIN_ORDER_AMOUNT_USDT = 5  # 例: 取引所の最小注文額


def is_valid_order(price, quantity):
    if quantity is None or quantity <= 0:
        print(f"[WARN] quantityが0以下のためスキップします: quantity={quantity}")
        return False
    if price * quantity < MIN_ORDER_AMOUNT_USDT:
        print(
            f"[WARN] 注文額が最低注文額未満のためスキップします: price={price} quantity={quantity} 合計={price*quantity}"
        )
        return False
    return True


def main():
    print("[INFO] Excelファイルを開きます...")
    app = xw.App(visible=False)
    wb = app.books.open(excel_path)

    try:
        print("[INFO] Buyシート（buy_orders）から読み込み:")
        buy_orders = read_orders_from_excel(excel_path, buy_sheet)
        for order in buy_orders:
            symbol, side, price, quantity, order_type = order
            if not is_valid_order(price, quantity):
                continue
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(*order)

        print("[INFO] Sellシート（sell_orders）から読み込み:")
        sell_orders = read_orders_from_excel(excel_path, sell_sheet)
        for order in sell_orders:
            symbol, side, price, quantity, order_type = order
            if not is_valid_order(price, quantity):
                continue
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(*order)

    finally:
        wb.close()
        app.quit()


if __name__ == "__main__":
    main()
