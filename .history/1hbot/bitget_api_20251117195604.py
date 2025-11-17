# bitget_api.py
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime, timezone

import requests



# ============================
# 署名生成
# ============================
def _sign(timestamp, method, path, body, secret_key):
    msg = f"{timestamp}{method}{path}{body}"
    mac = hmac.new(secret_key.encode(), msg.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


# ============================
# 認証付き（private API）
# ============================
def bitget_private_request(cfg, method, path, params=None, body_dict=None):
    base = cfg["bitget"]["base_url"]

    if params is None:
        params = {}
    if body_dict is None:
        body_dict = {}

    query = ""
    if params:
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())

    url = base + path + query
    body = json.dumps(body_dict) if body_dict else ""

    ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
    sign = _sign(ts, method, path + query, body, cfg["bitget"]["api_secret"])

    headers = {
        "ACCESS-KEY": cfg["bitget"]["api_key"],
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": ts,
        "ACCESS-PASSPHRASE": cfg["bitget"]["passphrase"],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.request(method, url, headers=headers, data=body, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    j = resp.json()
    if str(j.get("code")) not in ("00000", "0"):
        raise Exception(f"Bitget Error: {j}")

    return j


# ============================
# ポジション確認
# ============================
def get_current_position(cfg):
    symbol = cfg["trade"]["symbol"]
    margin_coin = cfg["trade"]["margin_coin"]

    endpoint = "/api/mix/v1/position/singlePosition"

    j = bitget_private_request(
        cfg,
        "GET",
        endpoint,
        params={"symbol": symbol, "marginCoin": margin_coin},
    )

    data = j.get("data")
    if not data:
        return False, None

    size = float(data.get("total", 0))
    if size > 0:
        return True, float(data.get("openPriceAvg", 0))
    return False, None


# ============================
# 注文実行
# ============================
def place_order(cfg, side, size, price=None):
    endpoint = "/api/mix/v1/order/placeOrder"

    body = {
        "symbol": cfg["trade"]["symbol"],
        "marginCoin": cfg["trade"]["margin_coin"],
        "size": str(size),
        "side": side,
        "orderType": "market",
        "leverage": str(cfg["trade"]["leverage"]),
    }

    j = bitget_private_request(
        cfg,
        "POST",
        endpoint,
        body_dict=body
    )
    return j
