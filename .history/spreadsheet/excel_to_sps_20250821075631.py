import os
import yaml
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定ファイルパス ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# --- config.yaml 読み込み ---
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# --- Google Sheets 情報 ---
spreadsheet_id = config["google_sheet"]["spreadsheet_id"]
sheet_name = config["google_sheet"]["excel_to_sps_sheet"]
creds_path = os.path.abspath(
    os.path.join(BASE_DIR, "..", config["google_sheet"]["creds_json"])
)

# --- Excel ファイルパス ---
excel_path = os.path.abspath(
    os.path.join(BASE_DIR, "..", config["order_export"]["source_file"])
)

# --- Google Sheets API 認証 ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# --- スプレッドシート取得 ---
spreadsheet = client.open_by_key(spreadsheet_id)

# --- Excel のデータ取得 ---
df = pd.read_excel(excel_path, sheet_name=sheet_name)

# --- 安全なシート名に変換 ---
safe_sheet_name = (
    sheet_name.replace(":", "_")
    .replace("/", "_")
    .replace("\\", "_")
    .replace("?", "_")
    .replace("*", "_")
    .replace("[", "_")
    .replace("]", "_")
)

try:
    # 既存シート取得
    worksheet = spreadsheet.worksheet(safe_sheet_name)
    # 既存データの末尾行を取得
    existing_data = worksheet.get_all_values()
    start_row = len(existing_data) + 1  # 追記開始行
    # 文字列化して送信
    # 文字列化して送信
    str_df = df.fillna("").astype(str)  # NaN を空文字に置換
    worksheet.update(
        values=[str_df.columns.tolist()] + str_df.values.tolist(),
        range_name=f"A{start_row}",
    )

    print(f"既存シート '{safe_sheet_name}' に追記しました。開始行: {start_row}")
except gspread.exceptions.WorksheetNotFound:
    # シートがなければ新規作成
    worksheet = spreadsheet.add_worksheet(
        title=safe_sheet_name, rows=df.shape[0] + 10, cols=df.shape[1] + 10
    )
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print(f"新規シート '{safe_sheet_name}' を作成して書き込みました。")

print("Excel → Google スプレッドシートへの書き込み（安全版）完了")
