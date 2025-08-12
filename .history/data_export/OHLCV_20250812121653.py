import requests
import pandas as pd
import datetime as dt
import time

symbol = "BTCUSDT"
interval = "30m"
limit = 1000  # Binanceの最大取得数
days_back = 365

end_time = int(dt.datetime.now().timestamp() * 1000)  # 現在時刻（ミリ秒）
start_time = end_time - days_back * 24 * 60 * 60 * 1000  # 1年前のミリ秒

all_data = []
current_time = start_time

print("データ取得開始...")

while current_time < end_time:
    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={interval}&limit={limit}&startTime={current_time}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        print(f"HTTPエラー: {response.status_code}")
        break

    data = response.json()
    if not data:
        print("データなし、終了")
        break

    all_data.extend(data)
    current_time = data[-1][0] + 1  # 次の開始時間に更新

    print(f"取得済みデータ数: {len(all_data)}本")

    # API過負荷回避のため少し待機（0.3秒）
    time.sleep(0.3)

print(f"総取得データ数: {len(all_data)}本")

# DataFrame作成
df = pd.DataFrame(
    all_data,
    columns=[
        "OpenTime", "Open", "High", "Low", "Close", "Volume",
        "CloseTime", "QuoteAssetVolume", "NumberOfTrades",
        "TakerBuyBaseVol", "TakerBuyQuoteVol", "Ignore"
    ]
)

# 時間をUTCのdatetime型に変換
df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit="ms", utc=True)
df["CloseTime"] = pd.to_datetime(df["CloseTime"], unit="ms", utc=True)

# 必要な列だけ抽出
df = df[["OpenTime", "Open", "High", "Low", "Close", "Volume"]]

# Excelに保存
output_file = f"{symbol}_{interval}_1year.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ ファイル保存完了: {output_file}")
