// API 配置
const API_BASE_URL = '/api';
const TOKEN_KEYS = ['auth_token', 'token'];

function getToken() {
    const token = localStorage.getItem(TOKEN_KEYS[0]) || localStorage.getItem(TOKEN_KEYS[1]);
    return token === 'null' || !token ? null : token;
}

let currentConversationId = null;
let allConversations = [];
let messageRefreshInterval = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    const token = getToken();
    if (!token) {
        alert('請先登入');
        window.location.href = '/'; // 重定向到登入頁面
        return;
    }

    loadConversations();
    // 每5秒刷新對話列表
    setInterval(loadConversations, 5000);
});

// ===== 對話列表功能 =====

function loadConversations() {
    const token = getToken();
    const conversationsList = document.getElementById('conversationsList');

    fetch(`${API_BASE_URL}/chat/conversations`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            conversationsList.innerHTML = `<div class="loading" style="color: #999;">加載失敗</div>`;
            return;
        }

        allConversations = data.conversations;
        renderConversationsList(data.conversations);
        updateUnreadCount();
    })
    .catch(error => {
        console.error('Error:', error);
        conversationsList.innerHTML = `<div class="loading" style="color: #999;">加載出錯</div>`;
    });
}

function renderConversationsList(conversations) {
    const conversationsList = document.getElementById('conversationsList');
    
    if (conversations.length === 0) {
        conversationsList.innerHTML = `
            <div style="padding: 20px; text-align: center; color: #999;">
                暫無對話
            </div>
        `;
        return;
    }

    conversationsList.innerHTML = conversations.map(conv => {
        const isActive = conv.id === currentConversationId ? 'active' : '';
        const unreadBadge = conv.unread_count > 0 ? 
            `<div class="unread-badge">${conv.unread_count}</div>` : '';
        
        return `
            <div class="conversation-item ${isActive}" onclick="selectConversation(${conv.id})">
                <div class="conversation-item-header">
                    <div>
                        <div style="font-weight: 600; color: #333;">對話 #${conv.id}</div>
                        <div style="font-size: 12px; color: #999;">
                            ${formatDate(conv.updated_at)}
                        </div>
                    </div>
                    ${unreadBadge}
                </div>
                <div class="conversation-item-preview">
                    ${conv.last_message || '暫無消息'}
                </div>
            </div>
        `;
    }).join('');
}

function selectConversation(conversationId) {
    currentConversationId = conversationId;
    
    // 更新 UI
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');

    // 隱藏 empty state
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('chatContainer').style.display = 'flex';

    // 加載聊天歷史
    loadChatHistory(conversationId);

    // 清除之前的計時器
    if (messageRefreshInterval) {
        clearInterval(messageRefreshInterval);
    }

    // 每3秒刷新消息
    messageRefreshInterval = setInterval(() => {
        loadChatHistory(conversationId);
    }, 3000);
}

// ===== 聊天功能 =====

function loadChatHistory(conversationId) {
    const token = getToken();
    const chatMessages = document.getElementById('chatMessages');

    fetch(`${API_BASE_URL}/chat/conversation/${conversationId}`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            chatMessages.innerHTML = `<div style="text-align: center; color: #999;">加載失敗</div>`;
            return;
        }

        renderChatMessages(data.messages);
        
        // 自動滾動到底部
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    })
    .catch(error => {
        console.error('Error:', error);
        chatMessages.innerHTML = `<div style="text-align: center; color: #999;">加載出錯</div>`;
    });
}

function renderChatMessages(messages) {
    const chatMessages = document.getElementById('chatMessages');

    chatMessages.innerHTML = messages.map(msg => {
        const messageClass = msg.message_type === 'user' ? 'user' : 'agent';
        const senderLabel = msg.message_type === 'user' ? '您' : '客服';

        return `
            <div class="message ${messageClass}">
                <div>
                    <div class="message-content">${escapeHtml(msg.message)}</div>
                    <div class="message-time">
                        ${senderLabel} • ${formatTime(msg.created_at)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (!message) {
        alert('請輸入消息');
        return;
    }

    if (!currentConversationId) {
        alert('請先選擇一個對話');
        return;
    }

    const token = getToken();
    const sendBtn = event.currentTarget;
    sendBtn.disabled = true;
    sendBtn.textContent = '發送中...';

    fetch(`${API_BASE_URL}/chat/send`, {
        method: 'POST',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            conversation_id: currentConversationId,
            message: message,
            type: 'user'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('發送失敗：' + data.message);
            return;
        }

        // 清空輸入框
        messageInput.value = '';

        // 重新加載消息
        loadChatHistory(currentConversationId);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('發送失敗');
    })
    .finally(() => {
        sendBtn.disabled = false;
        sendBtn.textContent = '發送';
    });
}

// ===== 新建對話函數 =====

function openNewChatModal() {
    document.getElementById('newChatModal').classList.add('show');
}

function closeNewChatModal() {
    document.getElementById('newChatModal').classList.remove('show');
    document.getElementById('subjectInput').value = '';
    document.getElementById('initialMessage').value = '';
    hideModalAlert();
}

function createNewChat() {
    const subject = document.getElementById('subjectInput').value.trim();
    const initialMessage = document.getElementById('initialMessage').value.trim();

    if (!initialMessage) {
        showModalAlert('請輸入初始消息', 'error');
        return;
    }

    const token = getToken();
    const createBtn = event.currentTarget;
    createBtn.disabled = true;
    createBtn.textContent = '創建中...';

    // 1. 先創建對話
    fetch(`${API_BASE_URL}/chat/start`, {
        method: 'POST',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            subject: subject || '新對話'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showModalAlert('創建失敗：' + data.message, 'error');
            createBtn.disabled = false;
            createBtn.textContent = '創建對話';
            return;
        }

        const conversationId = data.conversation_id;

        // 2. 發送初始消息
        return fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: {
                'Authorization': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: conversationId,
                message: initialMessage,
                type: 'user'
            })
        })
        .then(response => response.json())
        .then(res => {
            if (res.error) {
                showModalAlert('發送消息失敗', 'error');
                return;
            }

            // 成功
            closeNewChatModal();
            loadConversations();
            selectConversation(conversationId);
            showModalAlert('對話創建成功！', 'success');
        });
    })
    .catch(error => {
        console.error('Error:', error);
        showModalAlert('操作失敗', 'error');
    })
    .finally(() => {
        createBtn.disabled = false;
        createBtn.textContent = '創建對話';
    });
}

// ===== 工具函數 =====

function updateUnreadCount() {
    const token = getToken();

    fetch(`${API_BASE_URL}/chat/unread`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.error && data.unread_count > 0) {
            document.title = `客服聊天 (${data.unread_count})`;
        } else {
            document.title = '客服聊天';
        }
    })
    .catch(error => console.error('Error:', error));
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const yesterdayOnly = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate());

    if (dateOnly.getTime() === todayOnly.getTime()) {
        return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
    } else if (dateOnly.getTime() === yesterdayOnly.getTime()) {
        return '昨天';
    } else if (date.getFullYear() === today.getFullYear()) {
        return date.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' });
    } else {
        return date.toLocaleDateString('zh-TW');
    }
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showModalAlert(message, type) {
    const alert = document.getElementById('modalAlert');
    alert.textContent = message;
    alert.className = `alert show alert-${type}`;
}

function hideModalAlert() {
    const alert = document.getElementById('modalAlert');
    alert.className = 'alert';
}

// 按 Enter 鍵發送消息
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey && currentConversationId) {
        event.preventDefault();
        sendMessage();
    }
});

// 關閉模態框（點擊外部）
document.getElementById('newChatModal').addEventListener('click', function(event) {
    if (event.target === this) {
        closeNewChatModal();
    }
});
