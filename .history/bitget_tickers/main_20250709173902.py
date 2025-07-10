import requests
import csv


def get_ticker_list():
    url = "https://api.bitget.com/api/mix/v1/market/products"
    response = requests.get(url)
    data = response.json()

    if data.get("code") != "00000":
        print("API取得失敗:", data)
        return []

    tickers = [
        product["symbol"] for product in data.get("data", []) if "symbol" in product
    ]
    return tickers


def save_tickers_to_csv(tickers, filename="bitget_tickers.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol"])  # ヘッダー
        for t in tickers:
            writer.writerow([t])
    print(f"✅ CSV出力完了: {filename}")


if __name__ == "__main__":
    tickers = get_ticker_list()
    print("取得したティッカー数:", len(tickers))
    for t in tickers:
        print(t)

    save_tickers_to_csv(tickers)
