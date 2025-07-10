import math
import xlwings as xw

MIN_ORDER_AMOUNT_USDT = 5
TICK_SIZE_SHEET_NAME = "tick_size"  # 対応表シート名（Excelに合わせて変更）

def load_tick_sizes(wb):
    """
    Excelの対応表シートから銘柄ごとのtick size（価格刻み幅）を辞書で取得
    A列=シンボル, B列=tick size（例）
    """
    tick_dict = {}
    if TICK_SIZE_SHEET_NAME not in [s.name for s in wb.sheets]:
        print(f"[WARN] 対応表シートがありません: {TICK_SIZE_SHEET_NAME}")
        return tick_dict

    sheet = wb.sheets[TICK_SIZE_SHEET_NAME]
    last_row = sheet.api.UsedRange.Rows.Count

    for row in range(2, last_row + 1):
        symbol = sheet.range(f"A{row}").value
        tick_val = sheet.range(f"B{row}").value
        if not symbol or tick_val is None:
            continue
        try:
            tick = float(tick_val)
            tick_dict[symbol] = tick
        except Exception:
            print(f"[WARN] tick_sizeの変換エラー 行:{row} symbol:{symbol} tick:{tick_val}")
    return tick_dict


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


def adjust_price(symbol, price, tick_dict):
    """
    銘柄ごとのtick sizeに従い価格を切り捨て丸め
    tick sizeが見つからない場合はデフォルト0.00001を使用
    """
    if price is None:
        return None
    tick = tick_dict.get(symbol)
    if tick is None:
        tick = 0.00001
        print(f"[WARN] {symbol} のtick_sizeが見つかりません。デフォルト値 {tick} を使用します。")

    decimal_places = max(0, -int(math.floor(math.log10(tick))))
    adjusted = math.floor(price / tick) * tick
    adjusted = round(adjusted, decimal_places)
    return adjusted


def read_orders_from_sheet(wb, sheet_name):
    if sheet_name not in [s.name for s in wb.sheets]:
        print(f"[ERROR] シートが存在しません: {sheet_name}")
        return []

    sheet = wb.sheets[sheet_name]
    last_row = sheet.api.UsedRange.Rows.Count
    orders = []

    for row in range(2, last_row + 1):
        symbol = sheet.range(f"A{row}").value
        side = sheet.range(f"B{row}").value
        price = sheet.range(f"C{row}").value
        quantity = sheet.range(f"D{row}").value
        order_type = sheet.range(f"E{row}").value

        if not symbol:
            continue

        print(
            f"[DEBUG] Excel読み込み行{row}: {symbol}, {side}, {price}, {quantity}, {order_type}"
        )
        orders.append((symbol, side, price, quantity, order_type))

    return orders


def place_orders(client, wb, buy_sheet, sell_sheet):
    tick_dict = load_tick_sizes(wb)

    print("[INFO] Buyシートから読み込み:")
    buy_orders = read_orders_from_sheet(wb, buy_sheet)
    for order in buy_orders:
        symbol, side, price, quantity, order_type = order
        price = adjust_price(symbol, price, tick_dict)
        if price is None or not is_valid_order(price, quantity):
            continue
        print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
        client.place_order(symbol, side, price, quantity, order_type)

    print("[INFO] Sellシートから読み込み:")
    sell_orders = read_orders_from_sheet(wb, sell_sheet)
    if not sell_orders:
        print(f"[WARN] {sell_sheet} シートが空または存在しません。売り注文はスキップします。")
    else:
        for order in sell_orders:
            symbol, side, price, quantity, order_type = order
            price = adjust_price(symbol, price, tick_dict)
            if price is None or not is_valid_order(price, quantity):
                continue
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(symbol, side, price, quantity, order_type)
