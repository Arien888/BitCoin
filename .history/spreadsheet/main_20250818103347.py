import os
import yaml
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

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

# --- pandas DataFrame に変換 ---
df = pd.DataFrame(all_data[1:], columns=all_data[0])  # 先頭行をヘッダーに

# --- Excelに書き込む ---
df.to_excel(output_path, index=False)

print(f"非公開スプレッドシートを Excel に保存しました: {output_path}")
