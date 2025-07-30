import subprocess

# folder1のmain.pyを実行
p1 = subprocess.Popen(['python', 'mexc/main.py'])

# folder2のmain.pyを実行
p2 = subprocess.Popen(['python', 'bitget/main.py'])

# 両方の終了を待つ（必要に応じて）
p1.wait()
p2.wait()

p3 = subprocess.Popen(['python', 'update_excel/main.py'])