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
        