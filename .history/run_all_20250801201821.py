import subprocess

p7 = subprocess.Popen(['python', 'update_excel/kill_background.py'])
p7.wait()# エクセルバックグラウンドプロセスを終了

# # folder1のmain.pyを実行
# p1 = subprocess.Popen(['python', 'mexc/main.py'])

# # folder2のmain.pyを実行
# p2 = subprocess.Popen(['python', 'bitget/main.py'])
# # 両方の終了を待つ（必要に応じて）
# p1.wait()
# p2.wait()


# p3 = subprocess.Popen(['python', 'update_excel/main.py'])# エクセルアップデート
# p3.wait()

# p4 = subprocess.Popen(['python', 'export_value_excel/main.py'])
# p4.wait()# 発注用エクセルアップデート

p6 = subprocess.Popen(['python', 'bitget_auto_rial/futuer_all_cancel.py'])
p6.wait()# 予約全解除



p5 = subprocess.Popen(['python', 'bitget_auto_rial/main.py'])
p5.wait()# 発注







