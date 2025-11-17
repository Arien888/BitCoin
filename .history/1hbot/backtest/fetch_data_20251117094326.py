import requests
import pandas as pd
import time

BASE_URL = "https://api.bitget.com/api/v2/market"

def fetch_klines(symbol="BTCUSDT", granularity="1H", limit=1000):
    url = f"{BASE_URL}/candles?symbol={symbol}&granularity={granularity}&limit={limit}"
    r = requests.get(url)
    raw = r.json()["data"]
    df = pd.DataFrame(raw, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    
    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float,
    })
    return df.sort_values("ts")
