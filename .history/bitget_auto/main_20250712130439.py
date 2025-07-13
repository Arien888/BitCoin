import sys
import io
import os
import yaml
import xlwings as xw
from bitget_client import BitgetClient
from order_processor import place_orders  # ここをbitget_ordersからorder_processorへ変更

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

excel_path = config["excel"]["path"]
buy_sheet = config["excel"]["sheets"]["buy"]
sell_sheet = config["excel"]["sheets"]["sell"]
close_long_sheet = config["excel"]["sheets"].get("close_long")
close_short_sheet = config["excel"]["sheets"].get("close_short")


client = BitgetClient(
    key=config["bitget"]["api_key"],
    secret=config["bitget"]["api_secret"],
    passphrase=config["bitget"]["passphrase"],
    is_testnet=True,  # または False に切り替え可能
)


def main():
    print("[INFO] Excelファイルを開きます...")
    app = xw.App(visible=False)
    wb = None

    try:
        wb = app.books.open(excel_path)
        # place_ordersはwb（xlwingsのBookオブジェクト）を渡すのでそのままでOK
        place_orders(
            client, wb, buy_sheet, sell_sheet, close_long_sheet, close_short_sheet
        )

    except Exception as e:
        import traceback

        print(f"[ERROR] 処理中に例外が発生しました: {e}")
        print(traceback.format_exc())

    finally:
        if wb:
            try:
                wb.close()
            except Exception as e:
                print(f"[WARN] Excelファイルを閉じるときに失敗: {e}")
        app.quit()


if __name__ == "__main__":
    main()
