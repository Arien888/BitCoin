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

    exchange = ccxt.bitget(
        {
            "apiKey": api_key,
            "secret": api_secret,
            "password": api_passphrase,
            "enableRateLimit": True,
        }
    )

    # 現物口座
    exchange.options["defaultType"] = "spot"
    balance_spot = exchange.fetch_balance()

    # マージン口座
    exchange.options["defaultType"] = "margin"
    balance_margin = exchange.fetch_balance()

    # 価格は例としてBTC/USDTのみ取得
    ticker_btc = exchange.fetch_ticker("BTC/USDT")

    # 銘柄の集合を現物とマージン両方から取得してユニーク化
    symbols = set(balance_spot.get("total", {}).keys()) | set(balance_margin.get("total", {}).keys())

    data_list = []

    for symbol in symbols:
        spot_total = balance_spot["total"].get(symbol, 0)
        spot_free = balance_spot["free"].get(symbol, 0)
        margin_total = balance_margin["total"].get(symbol, 0)
        margin_free = balance_margin["free"].get(symbol, 0)

        # tickerはBTCだけ例示的に入れる
        ticker_last = ticker_btc["last"] if symbol == "BTC" else ""
        ticker_high = ticker_btc.get("high", "") if symbol == "BTC" else ""
        ticker_low = ticker_btc.get("low", "") if symbol == "BTC" else ""

        data_list.append(
            {
                "symbol": symbol,
                "spot_total": spot_total,
                "spot_free": spot_free,
                "margin_total": margin_total,
                "margin_free": margin_free,
                "ticker_last": ticker_last,
                "ticker_high": ticker_high,
                "ticker_low": ticker_low,
            }
        )

    fieldnames = [
        "symbol",
        "spot_total",
        "spot_free",
        "margin_total",
        "margin_free",
        "ticker_last",
        "ticker_high",
        "ticker_low",
    ]

    save_combined_csv("bitget_balances.csv", data_list, fieldnames)
    print("bitget_balances.csv に現物とマージンの資産情報を保存しました。")


if __name__ == "__main__":
    main()
