import sys
import io
import os
import yaml
import time
from bitget_client import BitgetClient
from futuer_all_cancel import cancel_all_orders_for_symbols

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  ←危険
sys.stdout.reconfigure(encoding="utf-8")  # 安全にUTF-8化

# 設定ファイルのパス
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

# 設定読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# BitgetClient インスタンス
client = BitgetClient(
    key=config["bitget"]["subaccount"]["api_key"],
    secret=config["bitget"]["subaccount"]["api_secret"],
    passphrase=config["bitget"]["subaccount"]["passphrase"],
    is_testnet=config["bitget"]["subaccount"].get("is_testnet", False),
)


def cancel_all_orders_for_symbols():
    for symbol in symbols:
        try:
            print(f"[INFO] {symbol} の全注文をキャンセル中...")
            res = client.cancel_all_orders(symbol=symbol, margin_coin="USDT")
            print(f"[OK] キャンセル結果: {res}")
        except Exception as e:
            print(f"[ERROR] {symbol} の注文キャンセルに失敗: {e}")
            import traceback

            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] エラー:\n{str(e)}\n{traceback.format_exc()}\n"
                )


if __name__ == "__main__":
    cancel_all_orders_for_symbols()
