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


def adjust_price(price, price_place):
    if price is None or price_place is None:
        return price
    factor = 10**price_place
    adjusted = (int(price * factor)) / factor
    return adjusted


def adjust_quantity(quantity, volume_place):
    if quantity is None or volume_place is None:
        return quantity
    factor = 10**volume_place
    adjusted = (int(quantity * factor)) / factor
    return adjusted


def process_sheet(client, sheet, default_side):
    print(f"process_sheet[INFO] シート「{sheet.name}」を処理中...")

    # A2から始まるテーブル（ヘッダーは1行目）を自動拡張して読む
    for row in sheet.range("A2").expand("table").value:
        if not row or len(row) < 4:
            continue

        symbol = row[0]
        side = row[1] or default_side
        price = row[2]
        quantity = row[3]

        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            print(f"[WARN] quantityが数値ではないためスキップします: {quantity}")
            continue
        order_type = row[4] if len(row) > 4 else "limit"

        if not symbol or not side or not price or not quantity:
            print(f"[WARN] 不完全なデータをスキップ: {row}")
            continue

        if quantity <= 0:
            print(f"[WARN] quantityが0以下のためスキップします: {quantity}")
            continue

        print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")
        try:
            client.place_order(symbol, side, price, quantity, order_type)
        except Exception as e:
            print(f"[ERROR] 発注失敗: {symbol} - {e}")
