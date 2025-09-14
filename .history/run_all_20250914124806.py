import subprocess
import time

# position update
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(
    ["python", "update_excel/open_and_wait_then_close.py", "writer_file"]
).wait()  # writer_fileをただ開いて閉じる

subprocess.Popen(["python", "mexc/main.py"]).wait()# mexc保有額取得
subprocess.Popen(["python", "bitget/main.py"]).wait()# bitget保有額取得
subprocess.Popen(["python", "bitget/main_sub_account.py"]).wait()# bitgetsubアカウント保有額取得
subprocess.Popen(["python", "bitbank/get_balance.py"]).wait()# bitbank保有額取得
subprocess.Popen(["python", "bybit/main.py"]).wait()# bybit保有額取得
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(
    ["python", "update_excel/open_and_wait_then_close.py", "source_file"]
).wait()  # crypto_ver2.2.xlsxをただ開いて閉じる
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(["python", "bitbank/now_value.py"]).wait()  # bitbank data update

# エクセルアップデート
subprocess.Popen(
    ["python", "update_excel/main.py"]
).wait()  # セルの再計算、クエリの更新
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了


subprocess.Popen(
    ["python", "spreadsheet/excel_to_sps.py"]
).wait()  # エクセルのデータをスプレッドシートに書き込む

# スプレッドシートが計算されるのを待つ
time.sleep(10)  # 秒数は必要に応じて調整

# スプレッドシート
subprocess.Popen(
    ["python", "spreadsheet/main.py"]
).wait()  # スプレッドシートのデータをエクセルに書き込む


# エクセルアップデート
subprocess.Popen(
    ["python", "update_excel/main.py"]
).wait()  # セルの再計算、クエリの更新
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了



subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了


# 解除
subprocess.Popen(["python", "mexc/auto_spot_cancel.py"]).wait()  # mexc spot オーダ- all cancel
subprocess.Popen(["python", "bitget_auto_rial/all_cancel_sub_account.py"]).wait()  # bitget subaccount(big margin)オーダー全キャンセル
subprocess.Popen(["python", "bitbank/cancel_all_orders.py"]).wait()  # bitbank spot cancel
subprocess.Popen(["python", "bitget_auto_rial/ccxt_spot_cancel_all.py"]).wait()  # bitget spot cancel オーダー
subprocess.Popen(["python", "bitget_auto_rial/futuer_all_cancel.py"]).wait()  # bitget(minimargin)の予約全解除
subprocess.Popen(["python", "bybit/cancell_all_orders.py"]).wait()  #bybit cancel

time.sleep(10)

subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了

# ern to spot
subprocess.Popen(
    ["python", "bitget_auto_rial/move_earn.py"]
).wait()  # bitget earn to spot

# # sub transfer
subprocess.Popen(
    ["python", "bitget_auto_rial/sub_transfer.py"]
).wait()  # bitget sub transfer

# # main transfer
subprocess.Popen(
    ["python", "bitget_auto_rial/transfer.py"]
).wait()  # bitget transfer




subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了

# 発注
subprocess.Popen(
    ["python", "mexc/auto_spot.py"]
).wait()  # mexc open close オーダー(btc eth以外)

time.sleep(60)
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(
    ["python", "bitget_auto_rial/subaccount_futures.py"]
).wait()  # bitget subaccount(big margin)オーダー

# # bitbank
subprocess.Popen(["python", "bitbank/spot_ccxt.py"]).wait()  # bitbank spot oder

subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(["python", "bybit/auto_spot.py"]).wait()  # bybit発注

subprocess.Popen(
    ["python", "bitget_auto_rial/ccxt_spot.py"]
).wait()  # bitget spotオーダー

time.sleep(60)
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(["python", "bitget_auto_rial/main.py"]).wait()  # bitget(minmargin)発注


