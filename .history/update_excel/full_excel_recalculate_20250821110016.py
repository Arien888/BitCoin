import yaml
from pathlib import Path
import win32com.client
import time
import pythoncom


def full_excel_recalculate(file_path):
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    try:
        wb = excel.Workbooks.Open(str(file_path))
        print("⏳ ファイルを開いたので 10 秒待機します...")
        time.sleep(10)

        # ✅ 全セル再計算
        print("🔄 全セル再計算を実行します...")
        excel.CalculateFullRebuild()

        # ✅ 計算完了まで待機
        retry = 0
        while excel.CalculationState != 0:  # 0=xlDone, 1=xlCalculating, 2=xlPending
            print(f"⏳ 再計算中... {retry * 5} 秒経過")
            pythoncom.PumpWaitingMessages()  # COM メッセージ処理
            time.sleep(5)
            retry += 1
            if retry > 120:  # 最大10分待つ
                print("⚠ 再計算が終了しないためタイムアウトしました")
                break

        print("✅ 再計算完了")

        # ✅ Save を冪等にリトライ
        for i in range(5):
            try:
                wb.Save()
                print("💾 保存に成功しました")
                break
            except Exception as e:
                print(f"⚠ Save 失敗 {i+1}/5: {e}")
                time.sleep(5)
        else:
            print("❌ Save に失敗しました")

        wb.Close(SaveChanges=False)
        print("📕 ワークブックを閉じました")

    finally:
        excel.Quit()
        print("👋 Excel を終了しました")

    print(f"✅ 完了: {file_path}")


def main():
    # ✅ 1階層上の config.yaml を読み込み
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    order_cfg = config["order_export"]
    src_file = (config_path.parent / order_cfg["source_file"]).resolve()

    # ✅ 処理実行
    full_excel_recalculate(src_file)


if __name__ == "__main__":
    main()
