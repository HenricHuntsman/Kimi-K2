// Local chat UI. Backend failures remain visible; model output is rendered as text.
let sending = false;

async function initializeApp() {
    try {
        const response = await fetch('/api/init');
        const stats = await response.json();
        if (!response.ok) throw new Error(stats.error || 'Initialization failed');
        document.getElementById('capCount').textContent = stats.total_capabilities;
        document.getElementById('docCount').textContent = stats.documents_loaded;
        document.getElementById('statusBadge').textContent = stats.backend === 'ollama' ? 'Local Ollama configured' : 'Demo';
        document.getElementById('backendNotice').textContent = stats.backend === 'ollama'
            ? `Requested model: ${stats.model}. A successful response is needed to verify inference.`
            : 'Demo echo only. Configure the local Ollama backend for model responses.';
        document.getElementById('sendButton').disabled = false;
    } catch (error) {
        document.getElementById('statusBadge').textContent = 'Configuration error';
        document.getElementById('statusMessage').textContent = error.message;
    }
}

function addMessage(text, type) {
    const messages = document.getElementById('chatMessages');
    const element = document.createElement('div');
    element.className = `${type}-message`;
    element.textContent = text;
    messages.appendChild(element);
    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message || sending) return;
    sending = true;
    document.getElementById('sendButton').disabled = true;
    addMessage(message, 'user');
    document.getElementById('statusMessage').textContent = 'Waiting for response…';
    try {
        const response = await fetch('/api/chat', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, mode: 'chat' })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
        if (typeof data.message !== 'string') throw new Error('Missing assistant response');
        addMessage(data.message, 'ai');
        input.value = '';
        document.getElementById('statusMessage').textContent = data.demo
            ? 'Demo echo; no inference.' : `Answered by ${data.model} via local Ollama. No tools executed.`;
    } catch (error) {
        addMessage(`Error: ${error.message}`, 'ai');
        document.getElementById('statusMessage').textContent = 'Request failed; input retained for retry.';
    } finally {
        sending = false;
        document.getElementById('sendButton').disabled = false;
    }
}

function updateTime() {
    document.getElementById('currentTime').textContent = new Date().toLocaleTimeString();
}

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    updateTime();
    setInterval(updateTime, 1000);
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('chatInput').addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
