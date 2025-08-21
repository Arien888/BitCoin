import yaml
from pathlib import Path
import time
import pythoncom
import win32com.client


def full_excel_recalculate(file_path, wait_before=10, wait_after=10):
    """Excelファイルを開いて全セル再計算して保存"""
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        wb = excel.Workbooks.Open(str(file_path))
        print(f"⏳ ファイルを開いたので {wait_before} 秒待機します...")
        time.sleep(wait_before)

        # ✅ 全セル再計算（完全再構築）
        excel.CalculateFullRebuild()
        print("✅ 全セル再計算を実行しました")

        print(f"⏳ 再計算後 {wait_after} 秒待機します...")
        time.sleep(wait_after)

        wb.Save()
        wb.Close(False)
        print(f"💾 保存して閉じました: {file_path}")
    finally:
        excel.Quit()

    print("✅ Excel 全セル再計算 完了！")


def main():
    # ✅ 1階層上のconfig.yamlを読み込み
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    order_cfg = config["order_export"]
    src_file = (config_path.parent / order_cfg["source_file"]).resolve()

    # ✅ 処理実行（元ファイルに対して）
    full_excel_recalculate(src_file)


if __name__ == "__main__":
    main()
