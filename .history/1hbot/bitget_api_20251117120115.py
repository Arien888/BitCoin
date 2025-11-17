# bitget_api.py
import hmac
import hashlib
import base64
import json
from datetime import datetime, timezone

import requests
import yaml


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ==============================
# 署名関連（private用）
# ==============================
def _sign_request(timestamp: str, method: str, request_path: str, body: str, secret_key: str) -> str:
    msg = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(secret_key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode("utf-8")


# ==============================
# Public GET
# ==============================
import requests

def bitget_public_get(cfg, path, params=None):
    base_url = cfg["bitget"]["base_url"]
    url = base_url + path

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    resp = requests.get(url, params=params, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    try:
        return resp.json()
    except:
        raise Exception(f"JSON parse error: {resp.text[:200]}")

    base_url = "https://api.bitget.com"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    url = base_url + path

    resp = requests.get(url, params=params, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    try:
        return resp.json()
    except:
        raise Exception(f"JSON Parse Error: {resp.text[:200]}")

    """
    認証不要のPublic API用 GET
    path 例: "/api/mix/v1/market/history-candles"
    """
    if params is None:
        params = {}

    base_url = cfg["bitget"]["base_url"].rstrip("/")   # "https://api.bitget.com"
    url = base_url + path

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    try:
        return resp.json()
    except Exception:
        raise Exception(f"JSON Parse Error: {resp.text[:200]}")


# ==============================
# Private（認証付き）
# ==============================
def bitget_private_request(
    cfg: dict,
    method: str,
    path: str,
    params: dict | None = None,
    body_dict: dict | None = None,
) -> dict:
    """
    認証付き API（GET / POST 両方対応）
    path 例: "/api/mix/v1/position/singlePosition"
    """
    base_url = cfg["bitget"]["base_url"].rstrip("/")
    api_key = cfg["bitget"]["api_key"]
    secret = cfg["bitget"]["api_secret"]
    passphrase = cfg["bitget"]["passphrase"]

    if params is None:
        params = {}
    if body_dict is None:
        body_dict = {}

    query = ""
    if params:
        # 署名に含めるので path + query の形にする
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())

    url = base_url + path + ("" if method.upper() == "POST" else "")
    body = json.dumps(body_dict) if body_dict else ""

    ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    sign = _sign_request(ts, method.upper(), path + query, body, secret)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": ts,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
    }

    if method.upper() == "GET":
        resp = requests.get(base_url + path, params=params, headers=headers, timeout=10)
    else:
        resp = requests.post(base_url + path, params=params, data=body, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    j = resp.json()
    if j.get("code") not in ("00000", 0, "0"):
        raise Exception(f"Bitget error: {j}")
    return j


# ==============================
# ポジション / 注文ラッパ
# ==============================
def get_current_position(cfg: dict) -> tuple[bool, float | None]:
    """
    ロングポジションを持っているかどうか簡易チェック
    戻り値: (has_position: bool, entry_price: float | None)
    """
    symbol = cfg["trade"]["symbol"]
    margin_coin = cfg["trade"]["margin_coin"]

    j = bitget_private_request(
        cfg,
        "GET",
        "/api/mix/v1/position/singlePosition",
        params={"symbol": symbol, "marginCoin": margin_coin},
    )

    data = j.get("data")
    if not data:
        return False, None

    size = float(data.get("total", 0))
    if size > 0:
        entry_price = float(data.get("openPriceAvg", 0))
        return True, entry_price
    return False, None


def place_order(cfg: dict, side: str, size: float) -> dict:
    """
    side: "open_long" or "close_long"
    成行注文のみ（orderType="market"）
    """
    symbol = cfg["trade"]["symbol"]
    margin_coin = cfg["trade"]["margin_coin"]
    leverage = cfg["trade"]["leverage"]

    body = {
        "symbol": symbol,
        "marginCoin": margin_coin,
        "size": str(size),
        "side": side,
        "orderType": "market",
        "leverage": str(leverage),
    }

    j = bitget_private_request(
        cfg,
        "POST",
        "/api/mix/v1/order/placeOrder",
        body_dict=body,
    )
    return j
