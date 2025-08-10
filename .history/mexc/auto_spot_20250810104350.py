import os
import yaml
import ccxt

# 設定ファイルのパスを組み立て
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# config.yaml 読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["mexc"]["apiKey"]
secret = config["mexc"]["secret"]

# MEXC クライアント作成
mexc = ccxt.mexc({
    "apiKey": api_key,
    "secret": secret
})

# 例1: 残高確認
balance = mexc.fetch_balance()
print(balance["USDT"])  # USDT残高だけ表示

# 例2: 指値注文（BTCを指定価格で購入）
symbol = "BTC/USDT"
amount = 0.001
price = 116000  # USDT
order = mexc.create_limit_buy_order(symbol, amount, price)
print(order)

# 例3: 成行売り注文（BTCを全部売る）
# btc_amount = balance["BTC"]["free"]  # 利用可能BTC
# if btc_amount > 0:
#     sell_order = mexc.create_market_sell_order(symbol, btc_amount)
#     print(sell_order)
