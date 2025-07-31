import time
import hmac
import hashlib
import requests
import json
from load_config import load_config

def generate_signature(api_secret, params: dict):
    """Generate HMAC SHA256 signature."""
    params_str = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
    return hmac.new(api_secret.encode('utf-8'), hashlib.sha256('utf-8'), hashlib.sha256).hexdigest()

def place_order(symbol,side, order_type, qty, price=None):
    config = load_config()
    api_key = config["bybit"]["key"]
    api_secret = config["bybit"]["secret"]
    url = "https://api.bybit.com/v2/private/order/create"