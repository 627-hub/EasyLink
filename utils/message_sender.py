import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32
HWND_BROADCAST = 0xFFFF

_stock_msg_id = None

def get_stock_msg_id():
    global _stock_msg_id
    if _stock_msg_id is None:
        _stock_msg_id = user32.RegisterWindowMessageW("Stock")
    return _stock_msg_id

def send_message_to_tongdaxin(hwnd, stock_code):
    code_str = str(stock_code)
    code_int = int(stock_code)
    prefix = 7 if code_str.startswith(('6', '5')) else 6
    wparam = prefix * 1000000 + code_int

    msg_id = get_stock_msg_id()
    if msg_id == 0:
        return False

    return user32.PostMessageW(HWND_BROADCAST, msg_id, wparam, 0) != 0

def send_message_generic(hwnd, message, wparam=0, lparam=0):
    result = user32.SendMessageW(hwnd, message, wparam, lparam)
    return result
