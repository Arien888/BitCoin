import xlwings as xw
from order_utils import is_valid_order, adjust_price, adjust_quantity, process_sheet


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


def place_orders(
    client,
    workbook,
    buy_sheet,
    sell_sheet,
    close_long_sheet=None,
    close_short_sheet=None,
):
    if buy_sheet in workbook.sheet_names:
        process_sheet(client, workbook.sheets[buy_sheet], "buy")
    if sell_sheet in workbook.sheet_names:
        process_sheet(client, workbook.sheets[sell_sheet], "sell")
    if close_long_sheet and close_long_sheet in workbook.sheet_names:
        process_sheet(client, workbook.sheets[close_long_sheet], "close_long")
    if close_short_sheet and close_short_sheet in workbook.sheet_names:
        process_sheet(client, workbook.sheets[close_short_sheet], "close_short")

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
