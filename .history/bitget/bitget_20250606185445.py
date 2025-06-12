import ccxt
import yaml
import csv


def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_multiple_dicts_to_csv(filename, dicts_with_headers):
    """
    複数の辞書を1つのCSVファイルにまとめて書く関数。
    dicts_with_headers は [(ヘッダー名, dict), ...] のリスト。
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for header, data in dicts_with_headers:
            writer.writerow([header])  # セクションタイトル的に書く
            writer.writerow(["key", "value"])
            for k, v in data.items():
                if isinstance(v, dict):
                    v = str(v)
                writer.writerow([k, v])
            writer.writerow([])  # 空行で区切り


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

    # balanceのtotal、freeとtickerの3つの辞書をまとめてCSVに保存
    dicts = [
        ("Balance Total", balance.get("total", {})),
        ("Balance Free", balance.get("free", {})),
        ("Ticker BTC/USDT", ticker),
    ]

    save_multiple_dicts_to_csv("bitget_data.csv", dicts)
    print("bitget_data.csv にデータを保存しました。")


if __name__ == "__main__":
    main()
