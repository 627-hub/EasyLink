import ctypes
import ctypes.wintypes
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

    def link(self, stock_code):
        hwnd = self.find_window()
        if not hwnd:
            raise Exception(f'{self.name}: 未找到窗口')

        user32.SetForegroundWindow(hwnd)

        import time
        time.sleep(0.1)

        VK_DELETE = 0x2E
        user32.keybd_event(VK_DELETE, 0, 0, 0)
        user32.keybd_event(VK_DELETE, 0, 0x0002, 0)

        for char in stock_code:
            vk = ord(char.upper()) if char.isalpha() else int(char) + 0x30 if char.isdigit() else 0
            if vk:
                user32.keybd_event(vk, 0, 0, 0)
                user32.keybd_event(vk, 0, 0x0002, 0)
            time.sleep(0.02)

        VK_RETURN = 0x0D
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, 0x0002, 0)

        return True
