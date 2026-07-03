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

    def _key(self, vk, down=True):
        flag = 0 if down else 0x0002
        user32.keybd_event(vk, 0, flag, 0)

    def _chord(self, *keys):
        for k in keys:
            self._key(k, True)
            time.sleep(0.01)
        for k in reversed(keys):
            self._key(k, False)
            time.sleep(0.01)

    def _type(self, text):
        for ch in text:
            vk = ord(ch.upper()) if ch.isalpha() else ord(ch) if ch.isdigit() else 0
            if vk:
                self._key(vk, True)
                time.sleep(0.01)
                self._key(vk, False)
                time.sleep(0.01)

    def link(self, stock_code):
        hwnd = self.find_window()
        if not hwnd:
            raise Exception(f'{self.name}: 未找到窗口')

        user32.SetForegroundWindow(hwnd)
        time.sleep(0.15)

        self._chord(0x11, 0x47)
        time.sleep(0.2)

        self._key(0x2E, True)
        self._key(0x2E, False)
        time.sleep(0.05)

        self._type(stock_code)

        self._key(0x0D, True)
        self._key(0x0D, False)
        return True
