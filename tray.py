import sys
import os
import threading
import webbrowser
import struct
import tempfile
import ctypes
import ctypes.wintypes

import win32gui
import win32con
import win32api

from app import app, start_scheduler
from config import HOST, PORT, load_stock_dict, parse_stock_code, LOG_PATH

WM_TRAYICON = win32con.WM_USER + 20
ID_TRAY_SHOW = 1001
ID_TRAY_UPDATE = 1002
ID_TRAY_LOG = 1003
ID_TRAY_DOCS = 1004
ID_TRAY_EXIT = 1005


def _hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)


def _gen_icon_bytes():
    w, h = 32, 32
    xor = bytearray()
    for y in range(h - 1, -1, -1):
        for x in range(w):
            dx, dy = x - w // 2, y - h // 2
            d = (dx * dx + dy * dy) ** 0.5
            if d < 11:
                xor.extend([0, 102, 255, 255])
            elif d < 13:
                xor.extend([255, 255, 255, 255])
            else:
                xor.extend([0, 0, 0, 0])

    and_mask = bytearray()
    for y in range(h):
        byte = 0
        for x in range(w):
            dx, dy = x - w // 2, y - h // 2
            d = (dx * dx + dy * dy) ** 0.5
            bit = 0 if d < 13 else 1
            byte = (byte << 1) | bit
            if x % 8 == 7:
                and_mask.append(byte)
                byte = 0
        if w % 8 != 0:
            and_mask.append(byte << (8 - w % 8))

    bih = struct.pack('<IiiHHIIiiII', 40, w, h * 2, 1, 32, 0, len(xor), 0, 0, 0, 0)
    img_data = bih + bytes(xor) + bytes(and_mask)
    header = struct.pack('<HHH', 0, 1, 1)
    entry = struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(img_data), 22)
    return header + entry + img_data


def _load_icon():
    ico_data = _gen_icon_bytes()
    tmp = tempfile.NamedTemporaryFile(suffix='.ico', delete=False)
    tmp.write(ico_data)
    tmp.close()
    try:
        hicon = win32gui.LoadImage(0, tmp.name, win32con.IMAGE_ICON, 32, 32,
                                   win32con.LR_LOADFROMFILE)
        os.unlink(tmp.name)
        return hicon
    except Exception:
        os.unlink(tmp.name)
    return win32gui.LoadIcon(0, win32con.IDI_APPLICATION)


class SystemTray:
    def __init__(self):
        self.hwnd = None
        self.nid = None
        self.server_thread = None

    def wndproc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_COMMAND:
            cmd = lparam
            if cmd == ID_TRAY_SHOW:
                self._show_status()
            elif cmd == ID_TRAY_UPDATE:
                threading.Thread(target=self._update_dict, daemon=True).start()
            elif cmd == ID_TRAY_LOG:
                self._open_log()
            elif cmd == ID_TRAY_DOCS:
                webbrowser.open(f'http://{HOST}:{PORT}/api/status')
            elif cmd == ID_TRAY_EXIT:
                self._quit()
        elif msg == WM_TRAYICON:
            if lparam == win32con.WM_RBUTTONUP:
                self._show_menu()
            elif lparam == win32con.WM_LBUTTONUP:
                self._show_status()
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _run_flask(self):
        start_scheduler()
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

    def start_server(self):
        self.server_thread = threading.Thread(target=self._run_flask, daemon=True)
        self.server_thread.start()

    def create(self):
        hinst = win32api.GetModuleHandle(None)
        wc = win32gui.WNDCLASS()
        wc.hInstance = hinst
        wc.lpszClassName = 'EasyLinkTrayClass'
        wc.lpfnWndProc = self.wndproc
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW
        class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            class_atom, 'EasyLink',
            win32con.WS_OVERLAPPEDWINDOW,
            0, 0, 0, 0, 0, 0, hinst, None
        )

        hicon = _load_icon()
        self.nid = (self.hwnd, 0,
                     win32gui.NIF_ICON | win32gui.NIF_TIP | win32gui.NIF_MESSAGE,
                     WM_TRAYICON, hicon, 'EasyLink 联动服务')
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self.nid)

        stock_count = len(load_stock_dict())
        self._notify(f'EasyLink 已启动 | {stock_count} 只股票 | 端口 {PORT}')
        win32gui.PumpMessages()

    def _show_menu(self):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_TRAY_SHOW, '显示状态')
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_TRAY_UPDATE, '更新词典')
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_TRAY_LOG, '查看日志')
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, '')
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_TRAY_DOCS, '打开API状态')
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, '')
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_TRAY_EXIT, '退出')
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu, win32con.TPM_RIGHTBUTTON,
                                 pos[0], pos[1], 0, self.hwnd, None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def _notify(self, text):
        if self.nid:
            self.nid = (self.nid[0], self.nid[1], self.nid[2], self.nid[3], self.nid[4], text)
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, self.nid)

    def _show_status(self):
        stock_dict = load_stock_dict()
        markets = {'A': 0, 'HK': 0, 'US': 0}
        for v in stock_dict.values():
            m, _ = parse_stock_code(v)
            markets[m] = markets.get(m, 0) + 1
        msg = (f'EasyLink 联动服务\n\n'
               f'A股: {markets.get("A", 0)} 只\n'
               f'港股: {markets.get("HK", 0)} 只\n'
               f'美股: {markets.get("US", 0)} 只\n'
               f'监听端口: {HOST}:{PORT}\n'
               f'服务状态: 运行中')
        win32gui.MessageBox(self.hwnd, msg, 'EasyLink', win32con.MB_OK | win32con.MB_ICONINFORMATION)

    def _open_log(self):
        if os.path.exists(LOG_PATH):
            os.startfile(LOG_PATH)
        else:
            win32gui.MessageBox(self.hwnd, '日志文件不存在', 'EasyLink', win32con.MB_OK | win32con.MB_ICONWARNING)

    def _update_dict(self):
        self._notify('正在更新词典...')
        try:
            from update_stock_list import update_dictionary
            ok = update_dictionary()
            self._notify(f'词典更新完成: {len(load_stock_dict())} 只' if ok else '词典更新失败')
        except Exception as e:
            self._notify(f'更新出错: {e}')

    def _quit(self):
        if self.nid:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self.nid)
        win32gui.PostQuitMessage(0)
        os._exit(0)


def main():
    _hide_console()
    tray = SystemTray()
    tray.start_server()
    tray.create()


if __name__ == '__main__':
    main()
