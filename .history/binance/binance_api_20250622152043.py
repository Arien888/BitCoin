import time
import hmac
import hashlib
import requests

def get_binance_account(api_key, api_secret, base_url='https://api.binance.com'):
    endpoint = '/api/v3/account'
    timestamp = int(time.time() * 1000)
    query_string = f'timestamp={timestamp}'

    signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    url = f'{base_url}{endpoint}?{query_string}&signature={signature}'

    headers = {
        'X-MBX-APIKEY': api_key
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
