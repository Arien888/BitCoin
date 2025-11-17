# bitget_api.py
import requests

def bitget_public_get(cfg, path, params=None):
    if params is None:
        params = {}

    base = cfg["bitget"]["base_url"]
    url = base + path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    resp = requests.get(url, params=params, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    try:
        return resp.json()["data"]
    except:
        # futures 最新版は data ではなく、list 直接の場合がある
        return resp.json()


def get_current_position(cfg):
    """
    ロングポジションを持っているかどうかを返す簡易版。
    実際には position API を叩いて size を見に行く。
    """
    import requests
    import json

    base_url = cfg["bitget"]["base_url"]
    symbol = cfg["trade"]["symbol"]
    margin_coin = cfg["trade"]["margin_coin"]
    
    endpoint = "/api/mix/v1/position/singlePosition"
    url = base_url + endpoint

    params = {"symbol": symbol, "marginCoin": margin_coin}

    # 認証付きリクエスト
    j = bitget_private_request(cfg, "GET", endpoint, params=params)

    data = j.get("data")
    if not data:
        return False, None

    size = float(data.get("total", 0))
    if size > 0:
        entry_price = float(data.get("openPriceAvg", 0))
        return True, entry_price

    return False, None

def place_order(cfg, side, size, price=None):
    """
    side: "open_long" or "close_long"
    price: None → 成行
    """
    endpoint = "/api/mix/v1/order/placeOrder"

    body = {
        "symbol": cfg["trade"]["symbol"],
        "marginCoin": cfg["trade"]["margin_coin"],
        "size": str(size),
        "side": side,
        "orderType": "market",  # 成行
        "leverage": str(cfg["trade"]["leverage"])
    }

    j = bitget_private_request(
        cfg,
        "POST",
        endpoint,
        body_dict=body
    )
    return j
