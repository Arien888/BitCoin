import psutil
import win32gui
import win32process

def get_window_pids():
    """現在表示中の全ウィンドウのプロセスIDを取得"""
    pids = set()
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pids.add(pid)
    win32gui.EnumWindows(enum_handler, None)
    return pids

def kill_background_excel():
    visible_pids = get_window_pids()
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info["name"].lower() == 'excel.exe' and proc.info['pid'] not in visible_pids:
            try:
                proc.kill()
                print(f"✅ 背景のExcelプロセスを終了しました: {proc.info['pid']}")
            except psutil.NoSuchProcess:
                print(f"⚠️ プロセスが既に終了しています: {proc.info['pid']}")
            except psutil.AccessDenied:
                print(f"⚠️ アクセス拒否: {proc.info['pid']}")