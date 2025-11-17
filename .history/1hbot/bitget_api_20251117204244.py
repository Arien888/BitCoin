# bitget_api.py
import time
import hmac
import hashlib
import json
import requests


def _sign(timestamp, method, path, body, secret_key):
    msg = f"{timestamp}{method}{path}{body}"
    return hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def bitget_private_request(cfg, method, path, params=None, body_dict=None):
    api_key = cfg["bitget"]["api_key"]
    secret = cfg["bitget"]["api_secret"]
    passphrase = cfg["bitget"]["passphrase"]
    base_url = cfg["bitget"]["base_url"]

    if params is None:
        params = {}

    body = "" if body_dict is None else json.dumps(body_dict)

    timestamp = str(int(time.time() * 1000))

    sign = _sign(timestamp, method, path, body, secret)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

    url = base_url + path

    if method == "GET":
        resp = requests.get(url, headers=headers, params=params, timeout=10)
    else:
        resp = requests.post(url, headers=headers, data=body, timeout=10)

    j = resp.json()
    return j


# ====== PUBLIC GET ======
def bitget_public_get(cfg, path, params=None):
    base = cfg["bitget"]["base_url"]
    if params is None:
        params = {}
    url = base + path
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        raise Exception(f"HTTP {r.status_code}: {r.text}")
    return r.json().get("data")


# ====== POSITION ======
def get_current_position(cfg):
    """
    Futures のポジションを Bitget から取得して同期
    """
    symbol = cfg["trade"]["symbol"]
    margin = cfg["trade"]["margin_coin"]

    path = "/api/v2/mix/position/single-position-v2"

    params = {
        "symbol": symbol,
        "marginCoin": margin,
        "productType": "usdt-futures"
    }

    j = bitget_private_request(cfg, "GET", path, params=params)

    pos = j.get("data")
    if not pos:
        return False, None, 0.0

    size = float(pos["total"])
    entry_price = float(pos["openPriceAvg"]) if size > 0 else None

    has_pos = size > 0

    return has_pos, entry_price, size


# ====== ORDER ======
def place_order(cfg, side, size):
    """
    side = "open_long" / "close_long"
    size = 0.001 BTC など
    """
    symbol = cfg["trade"]["symbol"]
    margin = cfg["trade"]["margin_coin"]

    body = {
        "symbol": symbol,
        "marginCoin": margin,
        "size": str(size),
        "side": side,
        "orderType": "market",
        "productType": "usdt-futures"
    }

    path = "/api/v2/mix/order/place-order"

    return bitget_private_request(cfg, "POST", path, body_dict=body)
