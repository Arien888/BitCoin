import time
import hmac
import hashlib
import base64


class AuthHelper:
    def __init__(self, key, secret, passphrase, is_testnet=False):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.is_testnet = is_testnet

    def generate_signature(self, timestamp, method, request_path, body):
        message = f"{timestamp}{method.upper()}{request_path}{body}"
        mac = hmac.new(self.secret.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def make_headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time() * 1000))
        signature = self.generate_signature(timestamp, method, path, body)
        headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
        }
        if self.is_testnet:
            headers["paptrading"] = "1"
        return headers
