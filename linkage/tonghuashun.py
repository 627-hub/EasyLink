import ctypes
import ctypes.wintypes
import time
from .base import BaseLinker
from utils.window_finder import find_windows_by_title

user32 = ctypes.windll.user32

WM_CHAR = 0x0102
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

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

    def _find_input_edit(self, parent):
        """递归查找输入框子窗口"""
        child = user32.FindWindowExW(parent, 0, 'Edit', None)
        if child:
            return child
        child = user32.FindWindowExW(parent, 0, 'RichEdit20W', None)
        if child:
            return child
        child = user32.GetWindow(parent, 5)
        while child:
            ret = self._find_input_edit(child)
            if ret:
                return ret
            child = user32.GetWindow(child, 2)
        return None

    def _send_via_messages(self, hwnd, stock_code):
        """通过窗口消息发送股票代码（无需前台焦点）"""
        edit = self._find_input_edit(hwnd)
        if not edit:
            return False

        user32.SetFocus(edit)
        time.sleep(0.03)

        for ch in stock_code:
            user32.PostMessageW(edit, WM_CHAR, ord(ch.upper()), 0)
            time.sleep(0.01)

        user32.PostMessageW(edit, WM_KEYDOWN, 0x0D, 0)
        user32.PostMessageW(edit, WM_KEYUP, 0x0D, 0)
        return True

    def _send_via_keyboard(self, stock_code):
        """回退方案：模拟键盘输入"""
        hwnd = self.find_window()
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.1)

        user32.keybd_event(0x2E, 0, 0, 0)
        user32.keybd_event(0x2E, 0, 0x0002, 0)

        for ch in stock_code:
            vk = ord(ch.upper()) if ch.isalpha() else ord(ch) if ch.isdigit() else 0
            if vk:
                user32.keybd_event(vk, 0, 0, 0)
                user32.keybd_event(vk, 0, 0x0002, 0)
            time.sleep(0.02)

        user32.keybd_event(0x0D, 0, 0, 0)
        user32.keybd_event(0x0D, 0, 0x0002, 0)

    def link(self, stock_code):
        hwnd = self.find_window()
        if not hwnd:
            raise Exception(f'{self.name}: 未找到窗口')

        if not self._send_via_messages(hwnd, stock_code):
            self._send_via_keyboard(stock_code)

        return True
