import sys
import time
from app import app, linkers
from config import HOST, PORT, load_stock_dict

def test_stock_dict():
    print("=" * 50)
    print("测试股票词典")
    print("=" * 50)
    stock_dict = load_stock_dict()
    print(f"词典中共 {len(stock_dict)} 只股票")
    
    test_cases = [
        ("贵州茅台", "600519"),
        ("平安银行", "000001"),
        ("宁德时代", "300750"),
    ]
    
    for name, expected_code in test_cases:
        actual_code = stock_dict.get(name, "未找到")
        status = "✓" if actual_code == expected_code else "✗"
        print(f"  {status} {name}: {actual_code} (期望: {expected_code})")

def test_linkers():
    print("\n" + "=" * 50)
    print("测试联动模块")
    print("=" * 50)
    for name, linker in linkers.items():
        status = "运行中" if linker.is_running() else "未运行"
        print(f"  {linker.name}: {status}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_stock_dict()
        test_linkers()
    else:
        print(f"启动服务: {HOST}:{PORT}")
        app.run(host=HOST, port=PORT, debug=True)
