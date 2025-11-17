import requests
import pandas as pd

BASE_URL = "https://api.bitget.com/api/spot/v1/market/candles"

def fetch_klines(symbol="BTCUSDT_SPBL", period="1hour", limit=200):
    url = f"{BASE_URL}?symbol={symbol}&period={period}&limit={limit}"
    print("URL:", url)

    r = requests.get(url)
    print("Status code:", r.status_code)
    print("Raw text (first 200 chars):", r.text[:200])

    try:
        j = r.json()
    except Exception as e:
        print("JSON Parse Error:", e)
        return None

    if "data" not in j:
        print("Error: 'data' not in response:", j)
        return None

    raw = j["data"]

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


if __name__ == "__main__":
    df = fetch_klines()
    if df is not None:
        df.to_csv("btc_1h.csv", index=False)
        print("Saved -> btc_1h.csv")
