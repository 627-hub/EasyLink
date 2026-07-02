import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

EnumWindows = user32.EnumWindows
WndEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
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
    results = []
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            try:
                pids = [proc.pid]
                for pid in pids:
                    def callback(hwnd, lParam):
                        if IsWindowVisible(hwnd):
                            import win32process
                            _, pid_found = win32process.GetWindowThreadProcessId(hwnd)
                            if pid_found == pid:
                                results.append(hwnd)
                        return True
                    EnumWindows(WndEnumProc(callback), 0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return results
