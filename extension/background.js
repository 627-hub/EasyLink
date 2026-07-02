chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'LINK_STOCK') {
        fetch('http://127.0.0.1:3000/api/linkage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: request.code, name: request.name }),
        })
        .then(resp => resp.json())
        .then(data => sendResponse({ success: true, data }))
        .catch(err => sendResponse({ success: false, error: err.message }));
        return true;
    }
    if (request.type === 'GET_STOCK_DICT') {
        fetch('http://127.0.0.1:3000/api/stock-dict')
            .then(r => r.json())
            .then(data => { if (data && typeof data === 'object') sendResponse({ data }); else throw 'bad'; })
            .catch(() => {
                fetch(chrome.runtime.getURL('stock-data.json'))
                    .then(r => r.json())
                    .then(data => sendResponse({ data }))
                    .catch(() => sendResponse({ data: null }));
            });
        return true;
    }
});
