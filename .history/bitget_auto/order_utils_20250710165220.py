import math

MIN_ORDER_AMOUNT_USDT = 5

def load_tick_sizes(wb, tick_size_sheet_name="tick_size"):
    """
    Excelの対応表シートから銘柄ごとのtick size（価格刻み幅）を辞書で取得
    """
    tick_dict = {}
    if tick_size_sheet_name not in [s.name for s in wb.sheets]:
        print(f"[WARN] 対応表シートがありません: {tick_size_sheet_name}")
        return tick_dict

    sheet = wb.sheets[tick_size_sheet_name]
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
