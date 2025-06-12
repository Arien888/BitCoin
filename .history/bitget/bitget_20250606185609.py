import ccxt
import yaml
import csv


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_combined_csv(filename, data_list, fieldnames):
    """
    data_list: dictのリスト（各dictが1銘柄の情報）
    fieldnames: CSVのヘッダー（列名）
    """
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

    exchange = ccxt.bitget(
        {
            "apiKey": api_key,
            "secret": api_secret,
            "password": api_passphrase,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
    )

    balance = exchange.fetch_balance()
    ticker = exchange.fetch_ticker("BTC/USDT")

    # 銘柄一覧（balanceのtotalにある通貨）
    symbols = balance.get("total", {}).keys()

    data_list = []

    for symbol in symbols:
        # balance total と free を取得
        total = balance["total"].get(symbol, 0)
        free = balance["free"].get(symbol, 0)

        # tickerは取引ペアごとなので、ここでは例としてBTC/USDTだけ
        # 実際はペアごとにticker取得する必要あり
        ticker_last = ticker["last"] if symbol == "BTC" else ""
        ticker_high = ticker.get("high", "") if symbol == "BTC" else ""

        data_list.append(
            {
                "symbol": symbol,
                "balance_total": total,
                "balance_free": free,
                "ticker_last": ticker_last,
                "ticker_high": ticker_high,
            }
        )

    # 保存するCSVのカラム名
    fieldnames = ["symbol", "balance_total", "balance_free", "ticker_last", "ticker_high"]

    save_combined_csv("bitget_combined.csv", data_list, fieldnames)
    print("bitget_combined.csv に保存しました。")


if __name__ == "__main__":
    main()
