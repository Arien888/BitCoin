import subprocess

p7 = subprocess.Popen(["python", "update_excel/kill_background.py"])
p7.wait()  # エクセルバックグラウンドプロセスを終了

# folder1のmain.pyを実行
p1 = subprocess.Popen(["python", "mexc/main.py"])
p1.wait()

# folder2のmain.pyを実行
p2 = subprocess.Popen(["python", "bitget/main.py"])
p2.wait()


# p3 = subprocess.Popen(["python", "update_excel/main.py"])  # エクセルアップデート
# p3.wait()

p4 = subprocess.Popen(["python", "export_value_excel/main.py"])
p4.wait()  # 発注用エクセルアップデート

# p6 = subprocess.Popen(['python', 'bitget_auto_rial/futuer_all_cancel.py'])
# p6.wait()# bitget(minimargin)の予約全解除

p5 = subprocess.Popen(['python', 'bitget_auto_rial/main.py'])
p5.wait()# bitget(minmargin)発注

# p7 = subprocess.Popen(["python", "bybit/close_position.py"])
# p7.wait()  # bybit(bigmargin)ポジション全クローズ

p8 = subprocess.Popen(["python", "bybit/auto_future.py"])
p8.wait()  # bybit(bigmargin)オーダー
