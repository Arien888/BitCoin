from order_reader import read_orders_from_sheet, load_tick_sizes
from order_utils import is_valid_order, adjust_price, adjust_quantity, process_sheet


def send_orders_for_sheet(client, wb, sheet_name, price_places, volume_places):
    orders = read_orders_from_sheet(wb, sheet_name)
    if not orders:
        print(
            f"[WARN] {sheet_name} シートが空または存在しません。注文はスキップします。"
        )
        return

    for order in orders:
        symbol, side, price, quantity, order_type = order

        # price = adjust_price(price, price_places.get(symbol))
        # quantity = adjust_quantity(quantity, volume_places.get(symbol))

        if price is None or not is_valid_order(price, quantity):
            continue

        try:
            print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
            client.place_order(symbol, side, price, quantity, order_type)
        except Exception as e:
            print(f"[ERROR] 発注失敗: {symbol}, エラー: {e}")


def place_orders(
    client, wb, buy_sheet, sell_sheet, close_long_sheet=None, close_short_sheet=None
):
    sheet_names = [s.name for s in wb.sheets]

    price_places, volume_places = load_tick_sizes(wb, "a")

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
        send_orders_for_sheet(
            client, wb, close_short_sheet, price_places, volume_places
        )
