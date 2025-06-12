import ccxt
import yaml
import csv

def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_combined_csv(filename, data_list, fieldnames):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

def main():
    config = load_config()

    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]

    exchange = ccxt.bitget({
        "apiKey": api_key,
        "secret": api_secret,
        "password": api_passphrase,
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })

    balance = exchange.fetch_balance()
    tickers = exchange.fetch_tickers()  # すべてのペアの価格情報を一括取得

    symbols = balance.get("total", {}).keys()  # 保有銘柄リスト

    data_list = []

    for symbol in symbols:
        total = balance["total"].get(symbol, 0)
        free = balance["free"].get(symbol, 0)

        # 価格情報を探す：ここでは「シンボル/USDT」のペアがあればそれを使用
        pair = f"{symbol}/USDT"
        if pair in tickers:
            ticker_info = tickers[pair]
            ticker_last = ticker_info.get("last", "")
            ticker_high = ticker_info.get("high", "")
            ticker_low = ticker_info.get("low", "")
        else:
            ticker_last = ""
            ticker_high = ""
            ticker_low = ""

        data_list.append({
            "symbol": symbol,
            "balance_total": total,
            "balance_free": free,
            "ticker_last": ticker_last,
            "ticker_high": ticker_high,
            "ticker_low": ticker_low,
        })

    fieldnames = ["symbol", "balance_total", "balance_free", "ticker_last", "ticker_high", "ticker_low"]
    save_combined_csv("bitget_holdings.csv", data_list, fieldnames)
    print("bitget_holdings.csv に保存しました。")

if __name__ == "__main__":
    main()
