from .base import BaseLinker
from utils.window_finder import find_windows_by_title
from utils.message_sender import send_message_to_tongdaxin

class TongDaXinLinker(BaseLinker):
    def __init__(self):
        super().__init__('通达信')
        self.keywords = ['通达信']

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
        success = send_message_to_tongdaxin(hwnd, stock_code)
        if not success:
            raise Exception(f'{self.name}: 发送消息失败')
        return True
