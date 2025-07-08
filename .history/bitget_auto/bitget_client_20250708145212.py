# bitget_client.py

import time
import hmac
import hashlib
import base64
import json
import requests
from urllib.parse import urljoin

class BitgetClient:
    def __init__(self, key, secret, passphrase, base_url="https://api.bitget.com"):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.base_url = base_url

    def _generate_signature(self, timestamp, method, request_path, body):
        message = f"{timestamp}{method}{request_path}{body}"
        mac = hmac.new(self.secret.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def place_order(self, symbol, side, price, quantity, order_type):
        side_map = {"buy": "open_long", "sell": "open_short"}
        side = side_map.get(side.lower(), side)

        path = "/api/mix/v1/order/placeOrder"
        url = urljoin(self.base_url, path)
        timestamp = str(int(time.time() * 1000))

        body_dict = {
            "marginCoin": "USDT",
            "productType": "UMCBL",
            "symbol": symbol,
            "side": side.upper(),
            "orderType": order_type.upper(),
            "price": str(price) if order_type.lower() == "limit" else "",
            "size": str(quantity),
            "timeInForce": "GTC",
            "reduceOnly": False,
            "closeOrder": False,
            "positionId": 0,
            "visibleSize": "0",
            "externalOid": "",
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
