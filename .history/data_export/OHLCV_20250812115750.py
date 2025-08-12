import requests
import pandas as pd
import datetime as dt

symbol = "BTCUSDT"
interval = "1h"
limit = 1000  # Binanceの最大
days_back = 365

end_time = int(dt.datetime.now().timestamp() * 1000)  # ミリ秒
start_time = end_time - days_back * 24 * 60 * 60 * 1000

all_data = []
current_time = start_time

print("データ取得中...")

while current_time < end_time:
    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={interval}&limit={limit}&startTime={current_time}"
    )
    data = requests.get(url).json()

    if not data:
        break

    all_data.extend(data)
    current_time = data[-1][0] + 1  # 次の開始時間を更新
    print(f"取得: {len(all_data)} 本")

print(f"総データ数: {len(all_data)}")

# DataFrame化
df = pd.DataFrame(
    all_data,
    columns=[
        "OpenTime", "Open", "High", "Low", "Close", "Volume",
        "CloseTime", "QuoteAssetVolume", "NumberOfTrades",
        "TakerBuyBaseVol", "TakerBuyQuoteVol", "Ignore"
    ]
)

# 時間を人間向けに変換
df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit="ms")
df["CloseTime"] = pd.to_datetime(df["CloseTime"], unit="ms")

# 不要列を削除
df = df[["OpenTime", "Open", "High", "Low", "Close", "Volume"]]

# Excel出力
output_file = f"{symbol}_{interval}_1year.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ {output_file} に保存しました")
