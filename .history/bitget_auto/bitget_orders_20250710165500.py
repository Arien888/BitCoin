import xlwings as xw

MIN_ORDER_AMOUNT_USDT = 5


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


def load_tick_sizes(wb, sheet_name="bitget_futures_products"):
    price_places = {}
    volume_places = {}

    if sheet_name not in [s.name for s in wb.sheets]:
        print(f"[WARN] 対応表シートがありません: {sheet_name}")
        return price_places, volume_places

    sheet = wb.sheets[sheet_name]
    last_row = sheet.api.UsedRange.Rows.Count

    for row in range(2, last_row + 1):
        symbol = sheet.range(f"A{row}").value
        price_place = sheet.range(f"B{row}").value
        volume_place = sheet.range(f"C{row}").value

        if not symbol:
            continue

        try:
            price_places[symbol] = int(price_place)
            volume_places[symbol] = int(volume_place)
        except Exception:
            print(f"[WARN] 行 {row} の丸め桁数変換エラー symbol:{symbol}")

    return price_places, volume_places


def adjust_price(price, price_place):
    if price is None or price_place is None:
        return price
    factor = 10 ** price_place
    adjusted = (int(price * factor)) / factor
    return adjusted


def adjust_quantity(quantity, volume_place):
    if quantity is None or volume_place is None:
        return quantity
    factor = 10 ** volume_place
    adjusted = (int(quantity * factor)) / factor
    return adjusted


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

        print(
            f"[DEBUG] Excel読み込み行{row}: {symbol}, {side}, {price}, {quantity}, {order_type}"
        )
        orders.append((symbol, side, price, quantity, order_type))

    return orders


def place_orders(client, wb, buy_sheet, sell_sheet):
    # 対応表読み込み
    price_places, volume_places = load_tick_sizes(wb)

    print("[INFO] Buyシートから読み込み:")
    buy_orders = read_orders_from_sheet(wb, buy_sheet)
    for order in buy_orders:
        symbol, side, price, quantity, order_type = order

        price = adjust_price(price, price_places.get(symbol))
        quantity = adjust_quantity(quantity, volume_places.get(symbol))

        if price is None or not is_valid_order(price, quantity):
            continue

        print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
        client.place_order(symbol, side, price, quantity, order_type)

    print("[INFO] Sellシートから読み込み:")
    sell_orders = read_orders_from_sheet(wb, sell_sheet)
    if not sell_orders:
        print(
            f"[WARN] {sell_sheet} シートが空または存在しません。売り注文はスキップします。"
        )
    else:
        for order in sell_orders:
            symbol, side, price, quantity, order_type = order

            price = adjust_price(price, price_places.get(symbol))
            quantity = adjust_quantity(quantity, volume_places.get(symbol))

            if price is None or not is_valid_order(price, quantity):
                continue

            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(symbol, side, price, quantity, order_type)
