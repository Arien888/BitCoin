import subprocess

# position update
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(
    ["python", "update_excel/open_and_wait_then_close.py", "writer_file"]
).wait()  # writer_fileをただ開いて閉じる
# mexc保有額取得
subprocess.Popen(["python", "mexc/main.py"]).wait()
# bitget保有額取得
subprocess.Popen(["python", "bitget/main.py"]).wait()
# bitbank保有額取得
subprocess.Popen(["python", "bitbank/main.py"]).wait()
# bybit保有額取得
subprocess.Popen(["python", "bybit/main.py"]).wait()
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(
    ["python", "update_excel/open_and_wait_then_close.py", "source_file"]
).wait()  # crypto_ver2.2.xlsxをただ開いて閉じる
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了
subprocess.Popen(
    ["python", "bitbank/now_value.py"]
).wait()  # bitbank data update


# エクセルアップデート
subprocess.Popen(["python", "update_excel/main.py"]).wait()  # エクセルアップデート
subprocess.Popen(
    ["python", "update_excel/kill_background.py"]
).wait()  # エクセルバックグラウンドプロセスを終了

# minimargin
subprocess.Popen(
    ["python", "bitget_auto_rial/futuer_all_cancel.py"]
).wait()  # bitget(minimargin)の予約全解除
subprocess.Popen(["python", "bitget_auto_rial/main.py"]).wait()  # bitget(minmargin)発注

# spot
# mexc (btc以外の) spot order
subprocess.Popen(
    ["python", "mexc/auto_spot_cancel.py"]
).wait()  # mexc spot オーダ- all cancel
subprocess.Popen(
    ["python", "mexc/auto_spot.py"]
).wait()  # mexc open & close オーダー(btc以外)
# btc eth spot order
# # bitget spot
subprocess.Popen(
    ["python", "bitget_auto_rial/ccxt_spot_cancel_all.py"]
).wait()  # bitget spotオーダー(取引所移行のためcloseのみ)
subprocess.Popen(
    ["python", "bitget_auto_rial/ccxt_spot.py"]
).wait()  # bitget spotオーダー(取引所移行のためcloseのみ)


# big margin buy only

subprocess.Popen(
    ["python", "bitget_auto_rial/subaccount_futures.py"]
).wait()  # bitget subaccount(big margin)オーダー

# bitbank




# 手動発動
# bitbank
