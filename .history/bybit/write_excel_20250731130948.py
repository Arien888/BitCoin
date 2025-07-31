import pandas as pd
from openpyxl import load_workbook

def write_to_excel(data, file_path):
    try:
        book = load_workbook(file_path)
        
        account_data = data["result"]["list"][0]
        coin_list = account_data.pop("coin")

        # 基本情報
        account_info_df = pd.DataFrame([account_data])

        # コイン詳細
        coin_df = pd.DataFrame(coin_list)

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            account_info_df.to_excel(writer, sheet_name="bybit_account", index=False)
            coin_df.to_excel(writer, sheet_name="bybit_spot", index=False)

        print(f" excelファイルに書き込みました: {file_path}")

    except Exception as e:

        print(f"Excelへの書き込み中にエラーが発生しました: {e}")
