import time
import hmac
import hashlib
import requests
import urllib.parse

def get_bybit_spot_assets(api_key, api_secret, base_url='https://api.bybit.com'):
    endpoint = '/spot/v1/account'
    timestamp = str(int(time.time() * 1000))
    params = {
        'api_key': api_key,
        'timestamp': timestamp,
    }

    # クエリ文字列の作成（ソート済み）
    query_string = '&'.join([f"{k}={params[k]}" for k in sorted(params)])

    # 署名作成（HMAC SHA256）
    sign = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params['sign'] = sign

    url = f"{base_url}{endpoint}?{urllib.parse.urlencode(params)}"

    response = requests.get(url)
    response.raise_for_status()
    return response.json()
