import xlwings as xw
from order_utils import is_valid_order, adjust_price, adjust_quantity, process_sheet

def load_tick_sizes(wb, sheet_name="bitget_futures_products"):
    price_places = {}
    volume_places = {}

    sheet_names = [s.name for s in wb.sheets]
    if sheet_name not in sheet_names:
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
    sheet_names = [s.name for s in wb.sheets]
    if sheet_name not in sheet_names:
        print(f"[ERROR] シートが存在しません: {sheet_name}")
        return []

    sheet = wb.sheets[sheet_name]
    orders = []

    last_row = sheet.api.UsedRange.Rows.Count
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


def send_orders_for_sheet(client, wb, sheet_name, price_places, volume_places):
    orders = read_orders_from_sheet(wb, sheet_name)
    if not orders:
        print(f"[WARN] {sheet_name} シートが空または存在しません。注文はスキップします。")
        return

    for order in orders:
        symbol, side, price, quantity, order_type = order

        price = adjust_price(price, price_places.get(symbol))
        quantity = adjust_quantity(quantity, volume_places.get(symbol))

        if price is None or not is_valid_order(price, quantity):
            continue

        try:
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(symbol, side, price, quantity, order_type)
        except Exception as e:
            print(f"[ERROR] 発注失敗: {symbol}, エラー: {e}")


def place_orders(client, wb, buy_sheet, sell_sheet, close_long_sheet=None, close_short_sheet=None):
    sheet_names = [s.name for s in wb.sheets]

    price_places, volume_places = load_tick_sizes(wb)

    # シート処理
    if buy_sheet in sheet_names:
        process_sheet(client, wb.sheets[buy_sheet], "buy")
        send_orders_for_sheet(client, wb, buy_sheet, price_places, volume_places)
    if sell_sheet in sheet_names:
        process_sheet(client, wb.sheets[sell_sheet], "sell")
        send_orders_for_sheet(client, wb, sell_sheet, price_places, volume_places)
    if close_long_sheet and close_long_sheet in sheet_names:
        process_sheet(client, wb.sheets[close_long_sheet], "close_long")
        send_orders_for_sheet(client, wb, close_long_sheet, price_places, volume_places)
    if close_short_sheet and close_short_sheet in sheet_names:
        process_sheet(client, wb.sheets[close_short_sheet], "close_short")
        send_orders_for_sheet(client, wb, close_short_sheet, price_places, volume_places)
