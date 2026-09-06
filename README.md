# EasyLink (原 WzSLinker Improved)

基于 [WzSLinker](https://hrfocus.top/tutorial.html) V8.2 的改进版开源实现，包含优化的股票识别算法和全新的 Python 桌面端。

> **⚠️ 平台支持：仅 Windows**。联动层依赖 Win32 API（通达信 Stock 消息广播、同花顺键盘模拟、win32 窗口查找/托盘），行情软件联动仅在 Windows 桌面端可用。macOS 暂不支持，也无移植计划。

> 原作者 [祝先生Bruce](https://space.bilibili.com/354560516) 已有新进展，开发了功能更全面的**付费版本 WzSLinker V9.2**，支持更多功能与更好的体验，详见 [hrfocus.top](https://hrfocus.top/tutorial.html)。

## 下载

从本仓库的 [Releases 页面](../../releases) 下载预编译的 `EasyLink.exe`，解压即用，无需安装 Python。

## 自行构建

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller build.spec
```

构建产物在 `dist/` 目录。

## 项目结构

```
├── app.py                    # Flask 主应用
├── build.spec                # PyInstaller 构建配置
├── config.py                 # 配置管理
├── installer.iss             # Inno Setup 安装包脚本
├── requirements.txt          # Python 依赖
├── update_stock_list.py      # 股票词典更新脚本
├── data/
│   └── stock-data.json       # 股票词典 (名称→代码)
├── linkage/
│   ├── base.py               # 联动基类
│   ├── tongdaxin.py          # 通达信联动
│   ├── tonghuashun.py        # 同花顺联动
│   └── dongfangcaifu.py      # 东方财富联动
├── utils/
│   ├── window_finder.py      # 窗口查找工具
│   └── message_sender.py     # 消息发送工具
└── extension/                # 浏览器扩展 (Manifest V3)
    ├── manifest.json
    ├── content-script.js     # 核心识别算法
    ├── background.js
    ├── popup.html/js
    ├── icon16/48/128.png     # 像素风图标
    └── stock-data.json
```

## 快速开始

### 1. 安装 Python 依赖

```bash
cd wzslinker-dev
pip install -r requirements.txt
```

### 2. 更新股票词典

```bash
python update_stock_list.py
```

### 3. 启动桌面端服务

```bash
python app.py
```

服务将在 `http://127.0.0.1:3000` 启动

### 4. 安装浏览器扩展

1. 打开 Chrome/Edge，访问 `chrome://extensions/`
2. 开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `extension/` 目录

## 主要改进

### 股票识别算法

1. **减少误识别**
   - 使用负向断言 `(?<!\d)` 和 `(?!\d)` 防止匹配长数字
   - 上下文排除规则：过滤日期、电话、金额等

2. **动态词典更新**
   - 每日收盘后从东财 API 更新股票列表
   - 支持手动触发更新

3. **性能优化**
   - 本地 JSON 加载 <100ms
   - 后台静默更新，不阻塞页面

### 桌面端

1. **模块化设计**
   - 每个炒股软件独立模块
   - 易于扩展新软件

2. **REST API**
   - `/api/linkage` - 联动接口
   - `/api/stock-dict` - 获取股票词典
   - `/api/status` - 服务状态

## API 接口

### 联动股票

```bash
POST http://127.0.0.1:3000/api/linkage
Content-Type: application/json

{
    "code": "600519",
    "name": "贵州茅台"
}
```

### 获取股票词典

```bash
GET http://127.0.0.1:3000/api/stock-dict
```

### 获取状态

```bash
GET http://127.0.0.1:3000/api/status
```

## 开发说明

### 添加新的炒股软件联动

1. 在 `linkage/` 目录创建新文件
2. 继承 `BaseLinker` 类
3. 实现 `find_window()` 和 `link()` 方法
4. 在 `app.py` 中注册

### 修改识别算法

编辑 `extension/content-script.js` 中的 `ImprovedStockRecognizer` 类。

## 已知问题

- 同花顺和东方财富的联动使用模拟键鼠，需要软件在前台
- 指南针和大智慧模块待实现
