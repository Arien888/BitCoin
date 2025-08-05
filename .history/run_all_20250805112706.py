import subprocess

# p7 = subprocess.Popen(["python", "update_excel/kill_background.py"])
# p7.wait()  # エクセルバックグラウンドプロセスを終了

# p10 = subprocess.Popen(["python", "update_excel/open_and_wait_then_close.py", "writer_file"])
# p10.wait()#writer_fileをただ開いて閉じる

# # mexc保有額取得
# p1 = subprocess.Popen(["python", "mexc/main.py"])
# p1.wait()

# # # bitget保有額取得
# p2 = subprocess.Popen(["python", "bitget/main.py"])
# p2.wait()

# p7 = subprocess.Popen(["python", "update_excel/kill_background.py"])
# p7.wait()  # エクセルバックグラウンドプロセスを終了

p9 = subprocess.Popen(["python", "update_excel/open_and_wait_then_close.py", "source_file"])
p9.wait()#crypto_ver2.2.xlsxをただ開いて閉じる


# p7 = subprocess.Popen(["python", "update_excel/kill_background.py"])
# p7.wait()  # エクセルバックグラウンドプロセスを終了

# p3 = subprocess.Popen(["python", "update_excel/main.py"])  # エクセルアップデート
# p3.wait()

p7 = subprocess.Popen(["python", "update_excel/kill_background.py"])
p7.wait()  # エクセルバックグラウンドプロセスを終了

p4 = subprocess.Popen(["python", "export_value_excel/main.py"])
p4.wait()  # 発注用エクセルアップデート

# p6 = subprocess.Popen(["python", "bitget_auto_rial/futuer_all_cancel.py"])
# p6.wait()  # bitget(minimargin)の予約全解除

# p5 = subprocess.Popen(["python", "bitget_auto_rial/main.py"])
# p5.wait()  # bitget(minmargin)発注

# p7 = subprocess.Popen(["python", "bybit/close_position.py"])
# p7.wait()  # bybit(bigmargin)ポジション全クローズ

p11 = subprocess.Popen(["python", "bybit/cancel_all_orders.py"])
p11.wait()  # bybit(bigmargin)オーダー全キャンセル

p8 = subprocess.Popen(["python", "bybit/auto_future.py"])
p8.wait()  # bybit(bigmargin)オーダー
