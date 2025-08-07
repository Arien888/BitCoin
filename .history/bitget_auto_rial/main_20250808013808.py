import sys
import io
import os
import yaml
import xlwings as xw
from bitget_client import BitgetClient
from order_processor import place_orders  # bitget_orders → order_processor に変更
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# # 設定ファイルのパス
# CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

# スクリプトのあるディレクトリ（どこから実行されても同じになる）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# config.yaml の読み込み
with open(os.path.join(BASE_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Excel 関連設定
excel_rel_path = config["order_export"]["source_file"]
excel_path = excel_rel_path
buy_sheet = config["excel"]["sheets"]["buy"]
# sell_sheet = config["excel"]["sheets"]["sell"]
close_long_sheet = config["excel"]["sheets"].get("close_long")
# close_short_sheet = config["excel"]["sheets"].get("close_short")

# BitgetClient インスタンス化（テストネット切り替え対応）
client = BitgetClient(
    key=config["bitget"]["api_key"],
    secret=config["bitget"]["api_secret"],
    passphrase=config["bitget"]["passphrase"],
    is_testnet=config["bitget"].get("is_testnet", False),  # ← ここで切り替え
)


def main():
    print("[INFO] Excelファイルを開きます...")
    app = xw.App(visible=False)
    wb = None

    try:
        wb = app.books.open(excel_path)
        print("[INFO] Excelファイルを開きました。")

        time.sleep(5)  # 1秒待ってから次の処理へ

        place_orders(
            client,
            wb,
            buy_sheet,
            close_long_sheet,
        )
        print("[INFO] 注文処理が完了しました。")

    except Exception as e:
        import traceback

        print(f"[ERROR] 処理中に例外が発生しました: {e}")
        tb = traceback.format_exc()
        print(tb)
        # ログファイルに詳細を保存
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] エラー:\n{str(e)}\n{tb}\n")

    finally:
        if wb:
            try:
                wb.close()
            except Exception as e:
                print(f"[WARN] Excelファイルを閉じるときに失敗: {e}")
        app.quit()


if __name__ == "__main__":
    main()
