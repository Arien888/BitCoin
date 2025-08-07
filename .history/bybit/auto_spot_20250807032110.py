import time
import hmac
import hashlib
import requests
import json
from load_config import load_config  # config読み込みは同様に

config = load_config()

def place_spot_order(symbol, side, order_type, qty, price=None, time_in_force="GTC"):
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    url = "https://api.bybit.com/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    try:
        qty = float(qty)
        if price is not None:
            price = float(price)
    except (ValueError, TypeError):
        print(f"[WARN] {symbol} の価格または数量が数値に変換できません。price={price}, qty={qty} → スキップします。")
        return

    # 注文金額が5USDT未満なら発注しない
    if price is not None and qty * price < 5:
        print(f"スキップ: {symbol} → {qty}×{price} = {qty * price}USDT（5未満）")
        return

    body = {
        "category": "spot",  # 現物は "spot"
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "qty": str(qty),
        "timeInForce": time_in_force,
    }
    if order_type == "Limit" and price is not None:
        # 余計な0は落とす（先物の書き方に合わせる）
        body["price"] = f"{price:.10f}".rstrip("0").rstrip(".")

    body_str = json.dumps(body, separators=(",", ":"))  # コンパクトに

    # 署名用文字列作成
    origin_string = f"{timestamp}{api_key}{recv_window}{body_str}"
    signature = hmac.new(
        api_secret.encode(),
        origin_string.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json",
    }

    # 送信は data=body_str に注意
    response = requests.post(url, headers=headers, data=body_str)

    print(f"=== 注文: {symbol} {side} {order_type} {qty} @ {price} ===")
    print("レスポンス:", response.text)
    return response.json()

if __name__ == "__main__":
    for sheet_name in sheet_names:
        print(f"=== {sheet_name} シートの注文を処理 ===")
        orders = read_orders_from_excel(sheet_name)
        for order in orders:
            result = place_order(
                order["symbol"],
                order["side"],
                order["order_type"],
                order["qty"],
                order["price"],
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
