import time
import hmac
import hashlib
import base64
import json
import requests
from urllib.parse import urljoin


class BitgetClient:
    def __init__(self, key, secret, passphrase, is_testnet=False):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.is_testnet = is_testnet
        self.base_url = "https://api.bitget.com"

    def _generate_signature(self, timestamp, method, request_path, body):
        message = f"{timestamp}{method.upper()}{request_path}{body}"
        mac = hmac.new(self.secret.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def place_order(self, symbol, side, price, quantity, order_type):
        path = "/api/v2/mix/order/place-order"
        url = urljoin(self.base_url, path)
        timestamp = str(int(time.time() * 1000))

        body_dict = {
            "symbol": symbol,                   # 例: SBTCSUSDT
            "productType": "susdt-futures",     # デモ用
            "marginMode": "isolated",
            "marginCoin": "SUSDT",              # デモコイン
            "size": str(quantity),
            "price": str(price),
            "side": side,                       # "buy" or "sell"
            "tradeSide": "open",                # "open" or "close"
            "orderType": order_type,            # "limit" or "market"
            "force": "gtc",                     # 有効期間 (GTC)
            "clientOid": str(int(time.time() * 1000)),
            "reduceOnly": "NO",
            "presetStopSurplusPrice": "",
            "presetStopLossPrice": ""
        }

        body = json.dumps(body_dict)
        signature = self._generate_signature(timestamp, "POST", path, body)

        headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
        }

        if self.is_testnet:
            headers["paptrading"] = "1"  # デモ取引用フラグ

        print(f"[INFO] 発注中: {symbol}, {side}, {price}, {quantity}, {order_type}")

        try:
            res = requests.post(url, headers=headers, data=body, timeout=15)
            print("[DEBUG] ステータスコード:", res.status_code)
            print("[DEBUG] レスポンステキスト:", res.text)
            res.raise_for_status()
            data = res.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))

            with open("bitget_response_log.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n\n")

            return data

        except Exception as e:
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(str(e) + "\n")
            return None
