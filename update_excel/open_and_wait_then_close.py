import time
import yaml
from pathlib import Path
from openpyxl import load_workbook
import sys
import xlwings as xw
import win32com.client


def load_excel_path_from_config(key_name, file_key="source_file"):
    # 1階層上のconfig.yamlを読み込み
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if key_name not in config:
        raise KeyError(f"config.yamlに '{key_name}' セクションが見つかりません。")

    section_cfg = config[key_name]

    if file_key not in section_cfg:
        raise KeyError(f"'{key_name}' セクションに '{file_key}' キーがありません。")

    # source_file は絶対パスの可能性が高いので、そのままPath化
    if file_key == "source_file":
        src_file = Path(section_cfg[file_key])
    else:
        # output_fileはconfig.yamlのあるディレクトリ基準の相対パスとして扱う
        src_file = (config_path.parent / section_cfg[file_key]).resolve()

    return src_file

def open_and_wait_then_close(path, wait_seconds=30):
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    print(f"📂 ファイルを開いて待機: {path}")
    try:
        wb = excel.Workbooks.Open(str(path))

        print(f"📝 最初のシート名: {wb.Sheets [1].Name}")

        print(f"⏳ {wait_seconds}秒間待機中...（OneDriveの同期を待つ）")
        time.sleep(wait_seconds)

        wb.Save()
        wb.Close()
        print("✅ ファイルを保存して閉じました")
        
    except Exception as e:
        print(f"エラー発生: {e}")
    finally:
        excel.Quit()  # ← これでExcelプロセスごと終了

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "source_file"
    print(f"受け取った引数: {arg}")
    excel_path = load_excel_path_from_config("order_export", file_key=arg)
    open_and_wait_then_close(excel_path, wait_seconds=45)
