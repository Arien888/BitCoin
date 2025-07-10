from order_utils import load_tick_sizes, is_valid_order, adjust_price, read_orders_from_sheet

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
