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
    factor = 10 ** price_place
    adjusted = (int(price * factor)) / factor
    return adjusted


def adjust_quantity(quantity, volume_place):
    if quantity is None or volume_place is None:
        return quantity
    factor = 10 ** volume_place
    adjusted = (int(quantity * factor)) / factor
    return adjusted
