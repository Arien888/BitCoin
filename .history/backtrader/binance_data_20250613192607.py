import requests
import pandas as pd
from datetime import datetime


def fetch_binance_ohlcv(symbol="ETHUSDT", interval="1d", limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    res = requests.get(url, params=params)
    data = res.json()

    rows = []
    for item in data:
        print(item[:6])  # ここで最初の6要素を出力して、openがどうなっているかを確認
        # ミリ秒タイムスタンプ → UTC日時文字列（Backtraderのdtformatに合わせる）
        dt = datetime.utcfromtimestamp(item[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        open_, high, low, close, volume = map(float, item[1:6])
        rows.append(
            {
                "datetime": dt,  # Backtraderの標準列名に合わせてカラム名を変えた
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "openinterest": 0,  # Backtraderはopeninterest列も必要
            }
        )

    df = pd.DataFrame(rows)

    # CSV保存（Backtrader用）
    df.to_csv("binance_btc.csv", index=False)
    print("Saved to binance_btc_backtrader.csv")


fetch_binance_ohlcv()
