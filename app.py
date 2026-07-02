import json
import logging
import threading
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask import make_response
from config import HOST, PORT, load_stock_dict, save_stock_dict, LINKAGE_ENABLED, setup_logging, parse_stock_code, LOG_PATH
from linkage import TongDaXinLinker, TongHuaShunLinker, DongFangCaiFuLinker

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

linkers = {
    'tongdaxin': TongDaXinLinker(),
    'tonghuashun': TongHuaShunLinker(),
    'dongfangcaifu': DongFangCaiFuLinker(),
}

@app.route('/api/linkage', methods=['POST'])
def linkage():
    data = request.json
    if not data or 'code' not in data:
        return jsonify({'error': '缺少股票代码参数'}), 400

    stock_code = data['code']
    stock_name = data.get('name', '')

    logger.info(f'联动请求: {stock_code} ({stock_name})')

    results = {}
    for name, linker in linkers.items():
        if not LINKAGE_ENABLED.get(name, False):
            results[name] = {'success': False, 'error': '已禁用'}
            continue
        try:
            linker.link(stock_code)
            results[name] = {'success': True}
            logger.info(f'{linker.name}: 成功联动 {stock_code}')
        except Exception as e:
            results[name] = {'success': False, 'error': str(e)}
            logger.warning(f'{linker.name}: 联动失败 - {e}')

    return jsonify(results)

@app.route('/api/stock-dict', methods=['GET'])
def get_stock_dict():
    stock_dict = load_stock_dict()
    return jsonify(stock_dict)

@app.route('/api/status', methods=['GET'])
def status():
    stock_dict = load_stock_dict()
    markets = {'A': 0, 'HK': 0, 'US': 0}
    for v in stock_dict.values():
        m, _ = parse_stock_code(v)
        markets[m] = markets.get(m, 0) + 1
    status_info = {
        'version': '1.0.0',
        'stock_count': len(stock_dict),
        'market_count': markets,
        'linkers': {}
    }
    for name, linker in linkers.items():
        status_info['linkers'][name] = {
            'enabled': LINKAGE_ENABLED.get(name, False),
            'running': linker.is_running()
        }
    return jsonify(status_info)

@app.route('/api/update-dict', methods=['POST'])
def update_dict():
    try:
        from update_stock_list import update_dictionary
        update_dictionary()
        return jsonify({'success': True, 'message': '词典更新完成'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _scheduled_update():
    """定时任务：交易日下午自动更新词典"""
    import schedule as sched
    import time

    def job():
        logger.info('定时更新词典开始')
        try:
            from update_stock_list import update_dictionary
            ok = update_dictionary()
            logger.info(f'定时更新词典{"成功" if ok else "失败"}')
        except Exception as e:
            logger.error(f'定时更新词典异常: {e}')

    sched.every().monday.at('16:00').do(job)
    sched.every().tuesday.at('16:00').do(job)
    sched.every().wednesday.at('16:00').do(job)
    sched.every().thursday.at('16:00').do(job)
    sched.every().friday.at('16:00').do(job)

    logger.info('定时更新词典已安排：交易日 16:00')
    while True:
        sched.run_pending()
        time.sleep(60)


def start_scheduler():
    t = threading.Thread(target=_scheduled_update, daemon=True)
    t.start()


@app.route('/api/logs', methods=['GET'])
def get_logs():
    lines = int(request.args.get('lines', 200))
    if not os.path.exists(LOG_PATH):
        return jsonify({'logs': []})
    with open(LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
        all_lines = f.readlines()
        return jsonify({'logs': all_lines[-lines:]})

if __name__ == '__main__':
    logger.info(f'EasyLink 启动 - {HOST}:{PORT}')
    stock_dict = load_stock_dict()
    markets = {'A': 0, 'HK': 0, 'US': 0}
    for v in stock_dict.values():
        m, _ = parse_stock_code(v)
        markets[m] = markets.get(m, 0) + 1
    logger.info(f'股票词典: {len(stock_dict)} 只 (A股{markets.get("A",0)} 港股{markets.get("HK",0)} 美股{markets.get("US",0)})')
    start_scheduler()
    app.run(host=HOST, port=PORT, debug=False)
