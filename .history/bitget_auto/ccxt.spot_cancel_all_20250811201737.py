import os
import yaml
import ccxt
from openpyxl import load_workbook

# 設定ファイルのパス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# config.yaml 読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# APIキー等
api_key = config["bitget"]["api_key"]
secret = config["bitget"]["api_secret"]
password = config["bitget"]["passphrase"]  # Bitgetはパスワード必須

# Bitget クライアント作成
bitget = ccxt.bitget({
    "apiKey": api_key,
    "secret": secret,
    "password": password,  # Bitget固有
})

def cancel_all_spot_orders(exchange):
    print("現物の未約定注文をすべてキャンセルします...")

    # 現物シンボル一覧取得（load_markets）
    markets = exchange.load_markets()
    # 現物のみのシンボルを抽出（Bitgetは現物は '/USDT' や '/BTC' のペア）
    spot_symbols = [symbol for symbol, market in markets.items() if market['spot']]

    for symbol in spot_symbols:
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            for order in open_orders:
                order_id = order['id']
                try:
                    exchange.cancel_order(order_id, symbol)
                    print(f"キャンセル成功: {symbol} 注文ID: {order_id}")
                except Exception as cancel_e:
                    print(f"キャンセル失敗: {symbol} 注文ID: {order_id} エラー: {cancel_e}")
        except Exception as fetch_e:
            print(f"未約定注文取得失敗: {symbol} エラー: {fetch_e}")

# 実行例
cancel_all_spot_orders(bitget)
