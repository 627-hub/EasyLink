import ctypes
import ctypes.wintypes
import time
from .base import BaseLinker
from utils.window_finder import find_windows_by_title

user32 = ctypes.windll.user32

class DongFangCaiFuLinker(BaseLinker):
    def __init__(self):
        super().__init__('东方财富')
        self.keywords = ['东方财富']

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
        time.sleep(0.1)

        VK_CONTROL = 0x11
        VK_KEY_G = 0x47
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_KEY_G, 0, 0, 0)
        user32.keybd_event(VK_KEY_G, 0, 0x0002, 0)
        user32.keybd_event(VK_CONTROL, 0, 0x0002, 0)

        time.sleep(0.1)

        VK_DELETE = 0x2E
        user32.keybd_event(VK_DELETE, 0, 0, 0)
        user32.keybd_event(VK_DELETE, 0, 0x0002, 0)

        time.sleep(0.05)

        for char in stock_code:
            if char.isdigit():
                vk = int(char) + 0x30
                user32.keybd_event(vk, 0, 0, 0)
                user32.keybd_event(vk, 0, 0x0002, 0)
            time.sleep(0.02)

        VK_RETURN = 0x0D
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, 0x0002, 0)

        return True
