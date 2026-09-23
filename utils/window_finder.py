import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

WndEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

# 显式声明原型：64 位下 HWND 为 64 位，缺省 restype=c_int 会截断句柄
user32.EnumWindows.argtypes = [WndEnumProc, ctypes.wintypes.LPARAM]
user32.EnumWindows.restype = ctypes.wintypes.BOOL
user32.GetWindowTextW.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowTextLengthW.argtypes = [ctypes.wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.IsWindowVisible.argtypes = [ctypes.wintypes.HWND]
user32.IsWindowVisible.restype = ctypes.wintypes.BOOL
user32.FindWindowW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR]
user32.FindWindowW.restype = ctypes.wintypes.HWND

EnumWindows = user32.EnumWindows
GetWindowTextW = user32.GetWindowTextW
GetWindowTextLengthW = user32.GetWindowTextLengthW
IsWindowVisible = user32.IsWindowVisible
FindWindowW = user32.FindWindowW

def get_window_text(hwnd):
    length = GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

def find_window(class_name=None, window_name=None):
    hwnd = FindWindowW(class_name, window_name)
    if hwnd and IsWindowVisible(hwnd):
        return hwnd
    return None

def find_windows_by_title(keyword):
    results = []
    def callback(hwnd, lParam):
        if IsWindowVisible(hwnd):
            title = get_window_text(hwnd)
            if keyword in title:
                results.append(hwnd)
        return True
    EnumWindows(WndEnumProc(callback), 0)
    return results

def find_windows_by_process(process_name):
    import psutil
    import win32process
    target_pids = set()
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            target_pids.add(proc.pid)
    results = []
    if not target_pids:
        return results

    def callback(hwnd, lParam):
        if IsWindowVisible(hwnd):
            _, pid_found = win32process.GetWindowThreadProcessId(hwnd)
            if pid_found in target_pids:
                results.append(hwnd)
        return True

    EnumWindows(WndEnumProc(callback), 0)
    return results
