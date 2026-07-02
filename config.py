import os
import sys
import json
import logging
import logging.handlers

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

DATA_DIR = os.path.join(BASE_DIR, 'data')
STOCK_DICT_PATH = os.path.join(DATA_DIR, 'stock-data.json')
LOG_DIR = os.path.join(APP_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'easylink.log')

HOST = '127.0.0.1'
PORT = 3000

LINKAGE_ENABLED = {
    'tongdaxin': True,
    'tonghuashun': True,
    'dongfangcaifu': True,
    'zhinanzhen': True,
    'dazhihui': True,
}


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    ))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    # also add console handler so tray window still sees logs
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    root.addHandler(console)


def parse_stock_code(raw):
    """解析股票代码，返回 (market, code)。
    格式: "600519" → ('SH', '600519')
          "HK:00700" → ('HK', '00700')
          "US:AAPL" → ('US', 'AAPL')
    """
    if ':' in raw:
        parts = raw.split(':', 1)
        return parts[0].upper(), parts[1]
    code = raw.strip()
    if code.startswith(('6', '5', '68')):
        return 'SH', code
    return 'SZ', code
def load_stock_dict():
    """加载股票词典：优先加载用户更新版，其次加载内置版"""
    if getattr(sys, 'frozen', False):
        local_path = os.path.join(APP_DIR, 'data', 'stock-data.json')
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    if os.path.exists(STOCK_DICT_PATH):
        with open(STOCK_DICT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_stock_dict(data):
    """保存股票词典：写入用户数据目录"""
    if getattr(sys, 'frozen', False):
        save_dir = os.path.join(APP_DIR, 'data')
    else:
        save_dir = DATA_DIR
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'stock-data.json')
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
