import ccxt
import yaml
from csv_util import save_dict_to_csv

def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    api_key = config["bitget"]["key"]
    api_secret = config["bitget"]["secret"]
    api_passphrase = config["bitget"]["passphrase"]

    exchange = ccxt.bitget(
        {
            "apiKey": api_key,
            "secret": api_secret,
            "password": api_passphrase,  # bitgetでは passphrase と呼ぶことも
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},  # or 'swap' など取引タイプを指定
        }
    )

    balance = exchange.fetch_balance()
    print("Balance:")
    print(balance)
    save_dict_to_csv("balance_total.csv", balance.get("total", {}))
    save_dict_to_csv("balance_free.csv", balance.get("free", {}))

    # BTC/USDTの現在価格を取得（例）
    ticker = exchange.fetch_ticker("BTC/USDT")
    print("BTC/USDT Price:")
    print(ticker["last"])


if __name__ == "__main__":
    main()
