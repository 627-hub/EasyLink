import ctypes
import time
from .base import BaseLinker
from utils.window_finder import find_windows_by_title

user32 = ctypes.windll.user32

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

    def _press_key(self, vk):
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.015)
        user32.keybd_event(vk, 0, 0x0002, 0)
        time.sleep(0.015)

    def link(self, stock_code):
        hwnd = self.find_window()
        if not hwnd:
            raise Exception(f'{self.name}: 未找到窗口')

        user32.SetForegroundWindow(hwnd)
        time.sleep(0.12)

        self._press_key(0x11)
        self._press_key(0x47)
        time.sleep(0.15)

        self._press_key(0x2E)

        for ch in stock_code:
            vk = ord(ch.upper()) if ch.isalpha() else ord(ch) if ch.isdigit() else 0
            if vk:
                self._press_key(vk)

        self._press_key(0x0D)
        return True
