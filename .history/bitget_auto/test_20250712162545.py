import openpyxl

file_path = r"C:\Users\koichi\Documents\MyDocuments\My_work\My_Programing_work\BitCoin\bitget_auto\a.xlsx"

wb = openpyxl.load_workbook(file_path)
print("認識しているシート名一覧:")
for sheet in wb.sheetnames:
    print(f"- '{sheet}'")
