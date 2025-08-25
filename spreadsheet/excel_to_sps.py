import os
import yaml
import gspread
import pandas as pd
import time
import random
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定ファイルパス ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# --- config.yaml 読み込み ---
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# --- Google Sheets 情報 ---
google_cfg = config.get("google_sheet", {})
spreadsheet_id = google_cfg.get("spreadsheet_id")
sheet_name = google_cfg.get("excel_to_sps_sheet")
creds_path = os.path.abspath(
    os.path.join(BASE_DIR, "..", google_cfg.get("creds_json", ""))
)

# --- Excel ファイルパス ---
excel_cfg = config.get("order_export", {})
excel_path = os.path.abspath(
    os.path.join(BASE_DIR, "..", excel_cfg.get("source_file", ""))
)

if not spreadsheet_id or not sheet_name or not os.path.exists(excel_path):
    raise ValueError("config.yaml または Excel ファイルの設定に不備があります")

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
try:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
except ValueError:
    raise ValueError(f"Excel ファイルにシート '{sheet_name}' が見つかりません")

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
    worksheet = spreadsheet.worksheet(safe_sheet_name)
    worksheet.clear()  # 既存データ削除
except gspread.exceptions.WorksheetNotFound:
    worksheet = spreadsheet.add_worksheet(
        title=safe_sheet_name, rows=df.shape[0] + 10, cols=df.shape[1] + 10
    )

# --- リトライ付き更新関数 ---
def safe_update(worksheet, data, max_retries=5, base_delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            worksheet.update(data)
            print(f"[OK] update 成功 (試行 {attempt} 回目)")
            return True
        except gspread.exceptions.APIError as e:
            print(f"[WARN] APIError (試行 {attempt} 回目): {e}")
        except Exception as e:
            print(f"[ERROR] 予期せぬエラー (試行 {attempt} 回目): {e}")

        sleep_time = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
        print(f"{sleep_time:.1f} 秒待機してリトライします...")
        time.sleep(sleep_time)

    print("[FAIL] 最大リトライ回数に達しました")
    return False

# --- データ送信 ---
str_df = df.fillna("").astype(str)
data = [str_df.columns.tolist()] + str_df.values.tolist()
safe_update(worksheet, data)

print(f"シート '{safe_sheet_name}' にデータを書き込みました（上書き）")
