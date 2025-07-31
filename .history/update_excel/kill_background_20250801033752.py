import psutil

def kill_excel_background_processes():
    count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'EXCEL.EXE' in proc.info['name'].upper():
                print(f"🛑 終了対象: PID={proc.pid}, NAME={proc.info['name']}")
                proc.terminate()
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if count == 0:
        print("✅ 終了対象のExcelプロセスは見つかりませんでした。")
    else:
        print(f"✅ {count} 個のExcelプロセスを終了しました。")

if __name__ == "__main__":
    kill_excel_background_processes()
