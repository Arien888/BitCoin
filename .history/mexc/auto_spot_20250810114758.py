import os
import yaml
import ccxt

# 設定ファイルのパスを組み立て
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# config.yaml 読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["mexc"]["api_key"]
secret = config["mexc"]["api_secret"]
excel_rel_path = config["order_export"]["source_file"]


sheet_names = [
    config["excel"]["sheets"]["mexc_open_long_spot"],  # ロング用シート名
    # config["excel"]["sheets"]["bitget_close_long_spot"],  # ショート用シート名
]
# MEXC クライアント作成
mexc = ccxt.mexc({
    "apiKey": api_key,
    "secret": secret
})

# 例1: 残高確認
balance = mexc.fetch_balance()
print(balance["USDT"])  # USDT残高だけ表示

# 例2: 指値注文（BTCを指定価格で購入）
symbol = "BTC/USD1"
amount =0.001
price = 114312.2
order = mexc.create_limit_buy_order(symbol, amount, price)
print(order)

# markets = mexc.load_markets()
# print("Available symbols:", list(markets.keys()))