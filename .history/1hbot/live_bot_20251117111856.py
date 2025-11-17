import time
import hmac
import hashlib
import base64
import json
import os
from datetime import datetime, timezone

import requests
import pandas as pd
import yaml


# ==============================
# 設定読み込み
# ==============================
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ==============================
# Bitget 認証付きリクエスト
# ==============================
def sign_request(timestamp, method, request_path, body, secret_key):
    # Bitget の署名: base64(HMAC_SHA256(timestamp+method+path+body, secret))
    msg = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(secret_key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode("utf-8")


def bitget_private_request(cfg, method, path, params=None, body_dict=None):
    base_url = cfg["bitget"]["base_url"]
    api_key = cfg["bitget"]["api_key"]
    secret = cfg["bitget"]["api_secret"]
    passphrase = cfg["bitget"]["passphrase"]

    if params is None:
        params = {}
    if body_dict is None:
        body_dict = {}

    # クエリ文字列
    query = ""
    if params:
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())

    url = base_url + path + query
    body = json.dumps(body_dict) if body_dict else ""

    # ISO timestamp (BitgetはmsでもOKだがここではISO8601)
    ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    sign = sign_request(ts, method, path + query, body, secret)

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign,
        "ACCESS-TIMESTAMP": ts,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
    resp = requests.get(url, params=params, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")
    j = resp.json()
    if j.get("code") not in ("00000", 0, "0"):
        raise Exception(f"Bitget error: {j}")
    return j


def bitget_public_request(url: str, params: dict):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    try:
        return resp.json()
    except:
        raise Exception(f"JSON Parse Error: {resp.text[:200]}")

    base_url = cfg["bitget"]["base_url"]
    if params is None:
        params = {}
    query = ""
    if params:
        query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    url = base_url + path + query
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")
    return resp.json()


# ==============================
# データ取得: 1h 足
# ==============================
def fetch_1h_candles(cfg, limit=300):
    # Futures (UMCBL) のチャートは BTCUSDT を使う必要がある
    trade_symbol = cfg["trade"]["symbol"]        # ex: BTCUSDT_UMCBL
    symbol = trade_symbol.split("_")[0]          # → BTCUSDT

    # V2 の正しい Kline API
    j = bitget_public_request(
        cfg,
        "/v2/market/history-candles",
        params={
            "symbol": symbol,
            "granularity": 3600,
            "limit": limit
        }
    )

    data = j.get("data", [])
    if not data:
        raise Exception(f"No candle data: {j}")

    # V2 は list of dict
    df = pd.DataFrame(data)

    # 必須カラムが存在する前提
    # ts は "timestamp" で来る
    df["ts"] = pd.to_datetime(df["timestamp"], unit="ms")

    # 数値変換
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # 古い → 新しい順へ
    df = df.sort_values("ts").reset_index(drop=True)

    return df

    symbol = cfg["trade"]["symbol"]

    # V2 共通 candles（spot も futures も共通）
    j = bitget_public_request(
        cfg,
        "/api/v2/market/candles",
        params={
            "symbol": symbol,
            "granularity": 3600,  # 1h
            "limit": limit
        }
    )

    data = j.get("data", [])
    if not data:
        raise Exception(f"No candle data: {j}")

    # V2 の data は list of dict
    df = pd.DataFrame(data)

    # V2 のキーは以下の形式
    # {
    #   "open": "...",
    #   "high": "...",
    #   "low": "...",
    #   "close": "...",
    #   "volume": "...",
    #   "timestamp": "1710307200000"
    # }

    df["ts"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
    df = df.sort_values("ts").reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df

    symbol = cfg["trade"]["symbol"]

    # futures の Kline は limit ではなく size を使う
    j = bitget_public_request(
        cfg,
        "/api/mix/v1/market/candles",
        params={
            "symbol": symbol,
            "granularity": 3600,  # 1h
            "size": limit         # ← ここが重要！
        }
    )

    data = j.get("data", [])
    if isinstance(data, list) and data and isinstance(data[0], list):
        # futures は [open, high, low, close, ts] の順な場合があるので対応する
        # フォーマットを確認して動的に列名を決める
        row_len = len(data[0])
        if row_len == 6:
            # 典型的な futures candles: [open, high, low, close, volume, ts]
            df = pd.DataFrame(
                data,
                columns=["open", "high", "low", "close", "volume", "ts"]
            )
        elif row_len == 5:
            # [open, high, low, close, ts]
            df = pd.DataFrame(
                data,
                columns=["open", "high", "low", "close", "ts"]
            )
            df["volume"] = 0
        else:
            raise Exception(f"Unsupported candle format: {data[0]}")

        # ts の形式に応じて変換
        try:
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        except:
            df["ts"] = pd.to_datetime(df["ts"])

        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        return df.sort_values("ts").reset_index(drop=True)

    else:
        raise Exception(f"Unexpected candles format: {j}")

    symbol = cfg["trade"]["symbol"]

    # futures の正しい endpoint → candles
    j = bitget_public_request(
        cfg,
        "/api/mix/v1/market/candles",
        params={
            "symbol": symbol,
            "granularity": 3600,
            "size": limit
        }
    )

    data = j.get("data", [])
    if isinstance(data, list) and data and isinstance(data[0], list):
        # data: [ [timestamp, open, high, low, close, volume], ... ]
        df = pd.DataFrame(
            data,
            columns=["ts", "open", "high", "low", "close", "volume"]
        )

        # timestamp は ms ではなく "2024-11-28T10:00:00Z" 形式のことがあるため対応
        try:
            df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        except:
            df["ts"] = pd.to_datetime(df["ts"])

        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        df = df.sort_values("ts").reset_index(drop=True)
        return df

    else:
        raise Exception(f"Unexpected candles format: {j}")

    symbol = cfg["trade"]["symbol"]
    # mix futures 1h = granularity=3600
    j = bitget_public_request(
        cfg,
        "/api/mix/v1/market/history-candles",
        params={
            "symbol": symbol,
            "granularity": 3600,
            "limit": limit
        }
    )
    data = j.get("data", [])
    if isinstance(data, list) and data and isinstance(data[0], list):
        # data: [[ts, open, high, low, close, volume, quoteVolume], ...]
        df = pd.DataFrame(
            data,
            columns=["ts", "open", "high", "low", "close", "volume", "quoteVolume"]
        )
        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        df = df.sort_values("ts").reset_index(drop=True)
        return df
    else:
        raise Exception(f"Unexpected candles format: {j}")


# ==============================
# テクニカル計算
# ==============================
def compute_indicators(df, params):
    ma_period = params["ma_period"]
    range_lb = params["range_lb"]

    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    df = df.dropna().reset_index(drop=True)
    return df


# ==============================
# シグナル判定
# ==============================
def decide_signal(df, params, has_position, entry_price=None):
    """
    戻り値:
      "BUY" / "SELL" / "HOLD"
    """
    ma_period   = params["ma_period"]
    low_thr     = params["low_thr"]
    high_thr    = params["high_thr"]
    entry_ma_dc = params["entry_ma_dc"]
    tp_pct      = params["tp_pct"]
    sl_pct      = params["sl_pct"]

    # 最新の確定足
    last = df.iloc[-1]
    ma_value = last[f"ma{ma_period}"]

    # すでにポジションがある場合は、利確・損切り・MA超えなどをチェック
    if has_position and entry_price is not None:
        hit_tp = last["close"] >= entry_price * (1.0 + tp_pct)
        hit_sl = last["close"] <= entry_price * (1.0 - sl_pct)
        ma_cross = last["close"] > ma_value
        range_top = last["range_pos"] > high_thr

        if hit_tp or hit_sl or ma_cross or range_top:
            return "SELL"

        return "HOLD"

    # ノーポジの場合：買いエントリー判定
    buy_signal = (
        (not has_position)
        and (last["close"] < ma_value * (1.0 - entry_ma_dc))
        and (last["range_pos"] < low_thr)
        and (last["prev_dir_up"] is False)
    )

    if buy_signal:
        return "BUY"

    return "HOLD"


# ==============================
# Bitget: ポジション＆注文
# ==============================
def get_current_position(cfg):
    """
    ロングポジションを持っているかどうかを返す簡易版。
    実際には position API を叩いて size を見に行く。
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

    # data: { "total": "...", "available": "...", "openPriceAvg": "...", ... } 的な構造想定
    # size が 0 より大きければポジション保有とみなす
    size = float(data.get("total", 0))
    if size > 0:
        entry_price = float(data.get("openPriceAvg", 0))
        return True, entry_price
    return False, None


def calc_order_size(cfg, last_price):
    usdt = cfg["trade"]["order_size_usdt"]
    # size = USDT / price
    size = usdt / last_price
    return round(size, 4)  # 小数4桁程度に丸める


def place_order(cfg, side, size, price=None):
    """
    side: "open_long" or "close_long"
    orderType: "market" 固定（まずは成行でOK）
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
        "leverage": str(leverage)
    }
    # price は成行なので不要

    j = bitget_private_request(
        cfg,
        "POST",
        "/api/mix/v1/order/placeOrder",
        body_dict=body
    )
    return j


# ==============================
# ログ
# ==============================
def append_trade_log(action, side, size, price, extra=""):
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "trade_log.csv")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = f"{now},{action},{side},{size},{price},{extra}\n"

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("time,action,side,size,price,extra\n")
            f.write(row)
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write(row)


# ==============================
# メイン処理
# ==============================
def main():
    print("=== CONFIG PATH TEST ===")

    # 先に config を読み込む
    cfg = load_config()

    # 読み込んだ config をここで初めて使う
    print("BASE_URL:", cfg["bitget"]["base_url"])

    print("=== 1h BTCUSDT_UMCBL BOT (MA+Range+Prev) ===")
    print("mode.dry_run =", cfg["mode"]["dry_run"])

    # 1) 足データ取得
    df = fetch_1h_candles(cfg, limit=300)
    df = compute_indicators(df, cfg["strategy"])

    # 2) 現在のポジション確認
    has_pos, entry_price = get_current_position(cfg)
    print("has_position:", has_pos, "entry_price:", entry_price)

    # 3) シグナル判定
    last = df.iloc[-1]
    signal = decide_signal(df, cfg["strategy"], has_pos, entry_price)
    print("last_close:", last['close'], "signal:", signal)

    # 4) シグナルに応じて注文 or 何もしない
    if signal == "BUY" and not has_pos:
        size = calc_order_size(cfg, last["close"])
        print(f"[SIGNAL] BUY size={size}")

        if cfg["mode"]["dry_run"]:
            print("DRY RUN → 注文は出さずログのみ")
            append_trade_log("DRY_RUN", "open_long", size, last["close"])
        else:
            res = place_order(cfg, "open_long", size)
            print("ORDER RESPONSE:", res)
            append_trade_log("ORDER", "open_long", size, last["close"], extra=json.dumps(res))

    elif signal == "SELL" and has_pos:
        size = calc_order_size(cfg, last["close"])
        print(f"[SIGNAL] SELL size={size}")


if __name__ == "__main__":
    main()
