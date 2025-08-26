import subprocess
import time

# # position update
# subprocess.Popen(
#     ["python", "update_excel/kill_background.py"]
# ).wait()  # エクセルバックグラウンドプロセスを終了
# subprocess.Popen(
#     ["python", "update_excel/open_and_wait_then_close.py", "writer_file"]
# ).wait()  # writer_fileをただ開いて閉じる


# mexc保有額取得
# subprocess.Popen(["python", "mexc/main.py"]).wait()
# bitget保有額取得
# subprocess.Popen(["python", "bitget/main.py"]).wait()
# # bitgetsubアカウント保有額取得
# subprocess.Popen(["python", "bitget/main_sub_account.py"]).wait()

# # bitbank保有額取得
# subprocess.Popen(["python", "bitbank/get_balance.py"]).wait()
# # bybit保有額取得
# subprocess.Popen(["python", "bybit/main.py"]).wait()
# subprocess.Popen(
#     ["python", "update_excel/kill_background.py"]
# ).wait()  # エクセルバックグラウンドプロセスを終了
# subprocess.Popen(
#     ["python", "update_excel/open_and_wait_then_close.py", "source_file"]
# ).wait()  # crypto_ver2.2.xlsxをただ開いて閉じる
# subprocess.Popen(
#     ["python", "update_excel/kill_background.py"]
# ).wait()  # エクセルバックグラウンドプロセスを終了
# subprocess.Popen(["python", "bitbank/now_value.py"]).wait()  # bitbank data update

# エクセルアップデート
# subprocess.Popen(
#     ["python", "update_excel/main.py"]
# ).wait()  # セルの再計算、クエリの更新
# subprocess.Popen(
#     ["python", "update_excel/kill_background.py"]
# ).wait()  # エクセルバックグラウンドプロセスを終了


# subprocess.Popen(
#     ["python", "spreadsheet/excel_to_sps.py"]
# ).wait()  # エクセルのデータをスプレッドシートに書き込む

# スプレッドシートが計算されるのを待つ
# time.sleep(20)  # 秒数は必要に応じて調整

# # スプレッドシート
subprocess.Popen(
    ["python", "spreadsheet/main.py"]
).wait()  # スプレッドシートのデータをエクセルに書き込む


# エクセルアップデート
# subprocess.Popen(
#     ["python", "update_excel/full_excel_recalculate.py"]
# ).wait()  # セルの再計算
# subprocess.Popen(
#     ["python", "update_excel/kill_background.py"]
# ).wait()  # エクセルバックグラウンドプロセスを終了

# minimargin
# subprocess.Popen(
#     ["python", "bitget_auto_rial/futuer_all_cancel.py"]
# ).wait()  # bitget(minimargin)の予約全解除
# subprocess.Popen(["python", "bitget_auto_rial/main.py"]).wait()  # bitget(minmargin)発注
# time.sleep(5)      # 終了後さらに5秒待つ
# spot
# mexc (btc eth以外の) spot order
# subprocess.Popen(
#     ["python", "mexc/auto_spot_cancel.py"]
# ).wait()  # mexc spot オーダ- all cancel
# subprocess.Popen(
#     ["python", "mexc/auto_spot.py"]
# ).wait()  # mexc open & close オーダー(btc eth以外)
# time.sleep(5)      # 終了後さらに5秒待つ
# # btc eth spot order
# # # bitget spot
# subprocess.Popen(
#     ["python", "bitget_auto_rial/ccxt_spot_cancel_all.py"]
# ).wait()  # bitget spotオーダー
# subprocess.Popen(
#     ["python", "bitget_auto_rial/move_earn.py"]
# ).wait()  # bitget earn to spot
# subprocess.Popen(
#     ["python", "bitget_auto_rial/ccxt_spot.py"]
# ).wait()  # bitget spotオーダー




# # big margin buy only

# subprocess.Popen(
#     ["python", "bitget_auto_rial/subaccount_futures.py"]
# ).wait()  # bitget subaccount(big margin)オーダー

# # # bitbank
# subprocess.Popen(["python", "bitbank/cancel_all_orders.py"]).wait()  # bitbank spot cancel
# subprocess.Popen(["python", "bitbank/spot_ccxt.py"]).wait()  # bitbank spot oder