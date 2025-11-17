# bitget_api.py
import requests

def bitget_public_get(cfg, path, params=None):
    if params is None:
        params = {}

    base = cfg["bitget"]["base_url"]
    url = base + path

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    resp = requests.get(url, params=params, headers=headers, timeout=10)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    try:
        return resp.json()["data"]
    except:
        # futures 最新版は data ではなく、list 直接の場合がある
        return resp.json()


