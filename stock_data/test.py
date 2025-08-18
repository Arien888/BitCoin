import yfinance as yf
import pandas as pd

# 日経225 ETF で代替
ticker = "1321.T"  # 日経225連動ETF

# データ取得
data = yf.download(ticker, start="2015-01-01", end="2025-01-01")

# データが空でないか確認
if data.empty:
    print("データ取得失敗")
else:
    # 年ごとに分割してプリント
    for year, df in data.groupby(data.index.year):
        print(f"\n=== {year}年のデータ ===")
        print(df.head())
        print("...")
        print(df.tail())
