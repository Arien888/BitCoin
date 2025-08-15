import os
import yaml
import ccxt
import win32com.client as win32
from datetime import datetime

# --- 設定ファイル読み込み ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["bitbank"]["api_key"]
secret = config["bitbank"]["api_secret"]

excel_rel_path = config["order_export"]["writer_file"]
excel_path = os.path.abspath(os.path.join(BASE_DIR, "..", excel_rel_path))

# --- Bitbank クライアント作成 ---
bitbank = ccxt.bitbank({"apiKey": api_key, "secret": secret})

# --- 残高取得 ---
try:
    balance = bitbank.fetch_balance()
except Exception as e:
    print("残高取得エラー:", e)
    balance = {}

# --- Excel COM API で開く ---
excel = win32.gencache.EnsureDispatch("Excel.Application")
excel.Visible = False  # 非表示で操作
wb = excel.Workbooks.Open(excel_path)

# --- 新規シート作成（既存と同名なら削除） ---
now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
sheet_name = "bitbank_balance"  # 固定名

# 既存シートがあれば再利用、なければ新規作成
ws = None
for sheet in wb.Sheets:
    if sheet.Name == sheet_name:
        ws = sheet
        # 内容をクリア
        ws.Cells.Clear()
        break

if ws is None:
    ws = wb.Sheets.Add()
    ws.Name = sheet_name

# ヘッダー
ws.Cells(1, 1).Value = "銘柄"
ws.Cells(1, 2).Value = "数量"

# 残高書き込み
row = 2
for asset, amount in balance.get("total", {}).items():
    if amount and amount > 0:
        ws.Cells(row, 1).Value = asset
        ws.Cells(row, 2).Value = amount
        row += 1

# 保存して閉じる
wb.Save()
wb.Close()
excel.Quit()

print(f"Excelの新規シート '{sheet_name}' に残高を書き込みました（クエリ破壊なし）")
