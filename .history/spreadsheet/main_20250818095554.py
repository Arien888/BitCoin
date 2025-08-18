import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- 認証スコープ ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# --- サービスアカウントJSONで認証 ---
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- スプレッドシートを開く ---
spreadsheet_id = "スプレッドシートIDをここに貼る"
spreadsheet = client.open_by_key(spreadsheet_id)

# --- 特定シートを指定 ---
worksheet = spreadsheet.worksheet("シート名")

# --- シート全体を取得 ---
all_data = worksheet.get_all_values()

# --- pandas DataFrame に変換 ---
df = pd.DataFrame(all_data[1:], columns=all_data[0])  # 先頭行をヘッダーに

# --- Excelに書き込む ---
df.to_excel("sheet_output.xlsx", index=False)

print("スプレッドシートを Excel に出力しました")
