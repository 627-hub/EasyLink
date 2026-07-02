const statusEl = document.getElementById('status');
const infoEl = document.getElementById('info');

async function checkStatus() {
    try {
        const resp = await fetch('http://127.0.0.1:3000/api/status');
        const data = await resp.json();
        statusEl.textContent = '桌面端已连接';
        statusEl.className = 'status ok';
        infoEl.textContent = `股票数量: ${data.stock_count}`;
    } catch (e) {
        statusEl.textContent = '桌面端未连接';
        statusEl.className = 'status error';
        infoEl.textContent = '请启动 EasyLink 应用';
    }
}

checkStatus();
setInterval(checkStatus, 5000);
