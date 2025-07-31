import time
import hmac
import hashlib
import requests
import json
from load_config import load_config

def generate_signature(api_secret, params):
    """Generate HMAC SHA256 signature."""
    query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
    return hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()