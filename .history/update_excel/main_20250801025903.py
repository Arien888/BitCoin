import yaml
from pathlib import Path
import win32com.client
import time


def full_excel_refresh_and_recalculate(file_path):
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(str(file_path))
    print("⏳ 開いた後、同期完了のため180秒待機します...")
    time.sleep(180)  # ← 必要に応じて調整（5〜15秒）

    # ✅ 「すべてを更新」ボタンと同等（PowerQueryなど）
    wb.RefreshAll()
    time.sleep(10)
    # ✅ 非同期クエリの完了を待機
    excel.CalculateUntilAsyncQueriesDone()

    # ✅ 数式すべて再計算（依存関係も含め完全に再構築）
    excel.CalculateFullRebuild()
    wb.Save()
    time.sleep(10)  # 少し待つ（数秒程度が目安）
    wb.Save()
    wb.Close(False)
    excel.Quit()

    print(f"✅ Power Query更新 & 数式再計算 完了: {file_path}")


def main():
    # ✅ 1階層上のconfig.yamlを読み込み
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    order_cfg = config["order_export"]
    src_file = (config_path.parent / order_cfg["source_file"]).resolve()

    # ✅ 処理実行（元ファイルに対して）
    full_excel_refresh_and_recalculate(src_file)


if __name__ == "__main__":
    main()
