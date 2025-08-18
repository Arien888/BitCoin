import os
import yaml
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from openpyxl import load_workbook

# --- 設定ファイルのパス ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# --- config.yaml 読み込み ---
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# --- スプレッドシート情報 ---
spreadsheet_id = config["google_sheet"]["spreadsheet_id"]
sheet_name = config["google_sheet"]["sheet_name"]
creds_path = os.path.abspath(os.path.join(BASE_DIR, "..", config["google_sheet"]["creds_json"]))

# --- Excel出力先 ---
output_path = os.path.abspath(os.path.join(BASE_DIR, "..", config["order_export"]["writer_file"]))

# --- Google Sheets API 認証 ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# --- スプレッドシートとシート取得 ---
spreadsheet = client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet(sheet_name)

# --- シート全体取得 ---
all_data = worksheet.get_all_values()
df = pd.DataFrame(all_data[1:], columns=all_data[0])  # 先頭行をヘッダーに

# --- Excel に追記または上書き（既存シートを保持） ---
# Excel 禁止文字を置換して安全なシート名に
safe_sheet_name = sheet_name.replace(":", "_").replace("/", "_").replace("\\", "_")\
                            .replace("?", "_").replace("*", "_").replace("[", "_").replace("]", "_")

try:
    book = load_workbook(output_path)
except FileNotFoundError:
    book = None

with pd.ExcelWriter(output_path, engine="openpyxl", mode="a" if book else "w", if_sheet_exists="replace") as writer:
    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

print(f"スプレッドシート '{sheet_name}' を Excel に保存しました: {output_path}")
