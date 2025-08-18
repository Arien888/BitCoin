import yfinance as yf

# Nikkei 225 のティッカー
ticker = "^N225"

# 2015年〜2025年のデータ（日足）
data = yf.download(ticker, start="2015-01-01", end="2025-01-01")

# 各年ごとにデータをプリント
for year, df in data.groupby(data.index.year):
    print(f"\n=== {year}年のデータ ===")
    print(df.head())   # 最初の5行だけ表示（全表示だと長すぎる）
    print("...")
    print(df.tail())   # 最後の5行も表示
