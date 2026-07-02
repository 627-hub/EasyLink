import requests
import json
import os
import re
from datetime import datetime
from config import STOCK_DICT_PATH, DATA_DIR, load_stock_dict, save_stock_dict
from collections import OrderedDict

EASTMONEY_API = 'https://push2.eastmoney.com/api/qt/clist/get'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://quote.eastmoney.com/',
    'Accept': 'application/json, text/plain, */*',
}

def fetch_tqcenter_stocks():
    """从通达信API获取A股列表(最准确)"""
    try:
        from tqcenter import tq
    except ImportError:
        print('  tqcenter不可用')
        return {}
    try:
        tq.initialize(__file__)
        raw = tq.get_stock_list(market='5', list_type=1)
        tq.close()
    except Exception as e:
        print(f'  tqcenter请求失败: {e}')
        return {}

    SH_PREFIXES = ('600', '601', '603', '605', '688')
    SZ_PREFIXES = ('000', '001', '002', '003', '300', '301')
    ALL_PREFIXES = SH_PREFIXES + SZ_PREFIXES

    stocks = OrderedDict()
    for item in raw:
        if not isinstance(item, dict):
            continue
        code_raw = item.get('Code', '')
        name = item.get('Name', '').strip()
        parts = code_raw.strip().split('.')
        if len(parts) != 2:
            continue
        code, mkt = parts[0], parts[1]
        if len(code) != 6 or not code.startswith(ALL_PREFIXES):
            continue
        if not name:
            continue
        if (mkt == 'SH' and code.startswith(SH_PREFIXES)) or \
           (mkt == 'SZ' and code.startswith(SZ_PREFIXES)):
            if code not in stocks:
                stocks[code] = name
    return dict(stocks)

def fetch_eastmoney_stocks():
    """从东方财富获取全部A股列表"""
    all_stocks = {}

    market_filters = [
        'm:0+t:6',    # 深圳A股
        'm:0+t:80',   # 深圳A股(创业板)
        'm:1+t:2',    # 上海A股
        'm:1+t:23',   # 上海A股(科创板)
        'm:0+t:81+s:2048',  # 北交所
    ]

    for fs in market_filters:
        params = {
            'pn': 1,
            'pz': 5000,
            'fs': fs,
            'fields': 'f12,f14'
        }
        try:
            resp = requests.get(EASTMONEY_API, params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            if data.get('data') and data['data'].get('diff'):
                diff = data['data']['diff']
                if diff and len(diff) > 0:
                    sample = diff[0]
                    if not hasattr(fetch_eastmoney_stocks, '_debug_printed'):
                        print(f'  API返回格式示例: {type(sample).__name__} = {repr(sample)[:200]}')
                        fetch_eastmoney_stocks._debug_printed = True
                for item in diff:
                    if isinstance(item, dict):
                        code = item.get('f12', '')
                        name = item.get('f14', '')
                    elif isinstance(item, str):
                        parts = item.split(',')
                        if len(parts) >= 2:
                            code = parts[0]
                            name = parts[1]
                        else:
                            continue
                    else:
                        continue
                    if code and name and len(code) == 6:
                        all_stocks[name] = code
            else:
                print(f'  {fs}: data字段为空, 响应: {repr(data)[:300]}')
        except Exception as e:
            print(f'获取 {fs} 失败: {e}')

    return all_stocks

def fetch_sina_stocks():
    """从新浪获取股票列表(备用)"""
    all_stocks = {}
    pages = ['sh', 'sz']
    for page in pages:
        url = f'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=5000&sort=symbol&asc=1&node={page}_a&symbol=&_s_r_a=init'
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            text = resp.text
            if text.startswith('['):
                items = json.loads(text)
                for item in items:
                    code = item.get('code', '')
                    name = item.get('name', '')
                    if code and name and len(code) == 6:
                        all_stocks[code] = name
        except Exception as e:
            print(f'获取新浪 {page} 失败: {e}')
    return all_stocks


def update_dictionary():
    """更新本地股票词典"""
    print(f'[{datetime.now()}] 开始更新股票词典...')

    new_stocks = {}

    a_stocks = fetch_tqcenter_stocks()
    if not a_stocks:
        print('通达信API获取失败，尝试新浪API')
        a_stocks = fetch_sina_stocks()

    if a_stocks:
        for code, name in a_stocks.items():
            clean = name.replace(' ', '').replace('　', '')
            new_stocks[clean] = code
            stripped = clean
            for p in ['*ST', 'ST', 'XD', 'XR', 'DR', 'N', 'C', 'U', 'W']:
                if stripped.startswith(p):
                    stripped = stripped[len(p):]
                    break
            if stripped != clean and len(stripped) >= 2:
                new_stocks[stripped] = code

    if not new_stocks:
        print('所有数据源均失败，跳过更新')
        return False

    existing = load_stock_dict()
    existing.update(new_stocks)
    save_stock_dict(existing)

    print(f'[{datetime.now()}] 词典更新完成，共 {len(existing)} 只 A股')
    return True

if __name__ == '__main__':
    update_dictionary()
