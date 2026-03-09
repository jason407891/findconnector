# 聊天功能 (Chat Feature) 使用指南

## 概述
新增的聊天模組提供了用戶與客服之間的實時對話功能，包括消息存儲、對話歷史和未讀消息管理。

## 功能特性

### 1. 對話管理
- **創建對話**: 用戶可以與客服開始新的對話
- **多個對話**: 用戶可以同時進行多個對話
- **對話狀態**: 支持 open（開放）、closed（已關閉）、waiting（等待中）三種狀態

### 2. 消息功能
- **發送消息**: 用戶和客服都可以發送消息
- **消息類型區分**: user（用戶消息）、agent（客服消息）
- **已讀追蹤**: 自動追蹤消息是否已讀
- **時間戳記**: 每條消息都記錄發送時間

### 3. 通知管理
- **未讀計數**: 獲取未讀消息數量
- **自動標記**: 查看對話時自動將消息標記為已讀

## API 端點

### 1. 創建新對話
```
POST /api/chat/start
Authorization: <JWT_TOKEN>
Content-Type: application/json

{
    "subject": "產品問題" (可選)
}

回應:
{
    "ok": true,
    "conversation_id": 1,
    "created_at": "2024-03-09 14:30:00"
}
```

### 2. 發送消息
```
POST /api/chat/send
Authorization: <JWT_TOKEN>
Content-Type: application/json

{
    "conversation_id": 1,
    "message": "我想咨詢關於產品的問題",
    "type": "user" (可選，默認為 "user")
}

回應:
{
    "ok": true,
    "message_id": 1,
    "conversation_id": 1,
    "created_at": "2024-03-09 14:30:30"
}
```

### 3. 獲取所有對話列表
```
GET /api/chat/conversations?page=1
Authorization: <JWT_TOKEN>

回應:
{
    "conversations": [
        {
            "id": 1,
            "created_at": "2024-03-09 14:30:00",
            "updated_at": "2024-03-09 14:35:00",
            "last_message": "感謝您的咨詢。。。",
            "unread_count": 2
        }
    ],
    "page": 1,
    "total": 5,
    "pages": 1
}
```

### 4. 獲取對話歷史
```
GET /api/chat/conversation/1
Authorization: <JWT_TOKEN>

回應:
{
    "conversation_id": 1,
    "messages": [
        {
            "id": 1,
            "user_id": 123,
            "message": "您好，我有個問題",
            "message_type": "user",
            "created_at": "2024-03-09 14:30:00",
            "is_read": 1
        },
        {
            "id": 2,
            "user_id": 1,
            "message": "您好！請告訴我您的問題。",
            "message_type": "agent",
            "created_at": "2024-03-09 14:30:30",
            "is_read": 1
        }
    ],
    "total": 2
}
```

### 5. 標記對話為已讀
```
PUT /api/chat/conversation/1/read
Authorization: <JWT_TOKEN>

回應:
{
    "ok": true
}
```

### 6. 獲取未讀消息計數
```
GET /api/chat/unread
Authorization: <JWT_TOKEN>

回應:
{
    "unread_count": 3
}
```

## 數據庫結構

### conversations 表
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT | 主鍵 |
| user_id | INT | 用戶ID |
| user_email | VARCHAR(255) | 用戶提價 |
| subject | VARCHAR(255) | 對話主題 |
| status | ENUM | open/closed/waiting |
| created_at | DATETIME | 創建時間 |
| updated_at | DATETIME | 更新時間 |
| assigned_agent | VARCHAR(255) | 指派給的客服 |

### chat_messages 表
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT | 主鍵 |
| conversation_id | INT | 對話ID |
| user_id | INT | 用戶ID |
| message | LONGTEXT | 消息內容 |
| message_type | ENUM | user/agent |
| is_read | BOOLEAN | 是否已讀 |
| created_at | DATETIME | 創建時間 |

## 初始化

### 方式 1：使用遷移腳本
```python
from api.utils.migrations import init_chat_tables

init_chat_tables()
```

### 方式 2：手動執行 SQL
在 MySQL 中執行以下 SQL 語句：

```sql
-- 創建 conversations 表
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    status ENUM('open', 'closed', 'waiting') DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    assigned_agent VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 創建 chat_messages 表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    user_id INT NOT NULL,
    message LONGTEXT NOT NULL,
    message_type ENUM('user', 'agent') DEFAULT 'user',
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);
```

## 使用場景

### 場景 1：用戶發起對話
```python
# 1. 用戶創建新對話
POST /api/chat/start
{
    "subject": "產品配送問題"
}

# 2. 用戶發送消息
POST /api/chat/send
{
    "conversation_id": 1,
    "message": "我的訂單還沒收到"
}
```

### 場景 2：查看對話歷史
```python
# 1. 獲取對話列表
GET /api/chat/conversations

# 2. 點擊對話後，獲取歷史記錄
GET /api/chat/conversation/1

# 3. 自動標記為已讀
# (會在獲取歷史時自動執行)
```

### 場景 3：監控未讀消息
```python
# 定期檢查是否有新消息
GET /api/chat/unread

# 如果 unread_count > 0，提示用戶有新消息
```

## 進階功能建議

1. **即時通知** - 使用 WebSocket 實現實時消息推送
2. **文件上傳** - 支持在聊天中上傳圖片或文件
3. **客服端面板** - 建立客服管理後台以回復消息
4. **自動回復** - 設置自動回復規則（如下班時間提示）
5. **消息搜索** - 支持搜索歷史消息
6. **批量操作** - 支持批量關閉對話或轉移客服

## 注意事項

- 所有 API 端點都需要有效的 JWT token（除了用戶註冊和登入）
- 用戶只能看到自己的對話
- 消息自動按時間順序排列
- 客服消息自動標記為已讀（首次查看時）
