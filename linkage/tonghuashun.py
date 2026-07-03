import ctypes
import ctypes.wintypes
import time
from .base import BaseLinker
from utils.window_finder import find_windows_by_title

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

KEYEVENTF_KEYDOWN = 0
KEYEVENTF_KEYUP = 0x0002

VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_G = 0x47


def _key(vk, up=False):
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP if up else KEYEVENTF_KEYDOWN, 0)


class TongHuaShunLinker(BaseLinker):
    def __init__(self):
        super().__init__('同花顺')
        self.keywords = ['同花顺', 'ths']

    def find_window(self):
        for kw in self.keywords:
            windows = find_windows_by_title(kw)
            if windows:
                return windows[0]
        return None

    def _find_view(self, parent):
        """查找主视图子窗口用于 AttachThreadInput 设焦"""
        def cb(hwnd, lp):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, buf, 256)
            if 'AfxFrameOrView' in buf.value:
                views.append(hwnd)
            return True
        WndEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        views = []
        user32.EnumChildWindows(parent, WndEnumProc(cb), 0)
        return views[0] if views else None

    def link(self, stock_code):
        hwnd = self.find_window()
        if not hwnd:
            raise Exception(f'{self.name}: 未找到窗口')

        target_tid = user32.GetWindowThreadProcessId(hwnd, None)
        current_tid = kernel32.GetCurrentThreadId()

        attached = False
        if target_tid != current_tid:
            attached = bool(user32.AttachThreadInput(current_tid, target_tid, True))

        view = self._find_view(hwnd) if attached else None
        if view:
            user32.SetFocus(view)
            user32.SetActiveWindow(hwnd)
            time.sleep(0.02)

        if target_tid != current_tid and attached:
            user32.AttachThreadInput(current_tid, target_tid, False)

        user32.SetForegroundWindow(hwnd)
        time.sleep(0.03)

        _key(VK_CONTROL)
        _key(VK_G)
        time.sleep(0.01)
        _key(VK_G, True)
        _key(VK_CONTROL, True)

        time.sleep(0.1)

        _key(VK_CONTROL)
        _key(0x41)
        time.sleep(0.01)
        _key(0x41, True)
        _key(VK_CONTROL, True)
        time.sleep(0.03)

        for ch in stock_code:
            vk = ord(ch.upper()) if ch.isalpha() else ord(ch) if ch.isdigit() else 0
            if vk:
                _key(vk)
                time.sleep(0.005)
                _key(vk, True)
                time.sleep(0.005)

        _key(VK_RETURN)
        time.sleep(0.01)
        _key(VK_RETURN, True)

        return True
