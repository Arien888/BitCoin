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
        self.base_url = "https://api.bitget.com"  # 本番・デモ共通

    def _generate_signature(self, timestamp, method, request_path, body):
        message = f"{timestamp}{method.upper()}{request_path}{body}"
        mac = hmac.new(self.secret.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def _convert_to_demo_symbol(self, symbol: str) -> str:
        # 例: "SHIBUSDT_UMCBL" → "SSHIBUSDT" に変換
        if self.is_testnet:
            if symbol.endswith("_UMCBL"):
                base = symbol[:-6]  # "SHIBUSDT"
                return "S" + base.upper()
            # 必要に応じて他のシンボルも変換
        return symbol

    def place_order(self, symbol, side, price, quantity, order_type):
        # APIパスはv2ミックス先物の注文エンドポイント
        path = "/api/v2/mix/order/place-order"
        url = urljoin(self.base_url, path)
        timestamp = str(int(time.time() * 1000))

        # デモ用シンボルに変換
        symbol_for_api = self._convert_to_demo_symbol(symbol)

        # tradeSide判定（open/close）を簡易に推測
        # 実際はロジックにより変えるべき
        trade_side = "open"
        if side.lower() in ["close_long", "close_short"]:
            trade_side = "close"
            side_simple = "sell" if "close_short" else "buy"
        else:
            side_simple = side.lower()

        # body組み立て
        body_dict = {
            "symbol": symbol_for_api,
            "productType": "susdt-futures" if self.is_testnet else "umcbl",
            "marginMode": "isolated",
            "marginCoin": "SUSDT" if self.is_testnet else "USDT",
            "size": str(quantity),
            "price": str(price),
            "side": side_simple,       # "buy" or "sell"
            "tradeSide": trade_side,  # "open" or "close"
            "orderType": order_type.lower(),  # "limit" or "market"
            "force": "gtc",
            "clientOid": str(int(time.time() * 1000)),
            "reduceOnly": False,
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

        # デモ取引用ヘッダー追加
        if self.is_testnet:
            headers["paptrading"] = "1"

        print(f"[INFO] 発注中: {symbol_for_api}, {side_simple}, {price}, {quantity}, {order_type}")

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
