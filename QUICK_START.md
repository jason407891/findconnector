# 快速開始指南

## 前端頁面已準備完成！

系統現在包含了完整的前端页面供您使用：

### 📱 新增页面

| 頁面 | 路由 | 說明 | 所需角色 |
|------|------|------|--------|
| **聊天** | `/chat` | 與客服溝通 | 任何登入用戶 |
| **後台管理** | `/admin` | 管理用戶和產品 | Admin / Super Admin |

---

## 🚀 快速開始步驟

### 1. 確保後端已啟動
```bash
python findconnector_refactored.py
```

應該看到類似的輸出：
```
 * Running on http://127.0.0.1:3000
```

### 2. 初始化數據庫
在 Python 命令行中執行：
```python
from api.utils.migrations import init_all
init_all()
```

如果你看到「All migrations completed successfully!」表示成功。

### 3. 創建測試用戶

通過後端 API 或數據庫直接創建用戶：

```mysql
-- 創建普通用戶
INSERT INTO users (username, email, password_hash, company, role)
VALUES ('testuser', 'test@example.com', 'hashed_password', 'Test Company', 'user');

-- 創建管理員用戶
INSERT INTO users (username, email, password_hash, company, role)
VALUES ('admin', 'admin@example.com', 'hashed_password', 'Admin Company', 'admin');
```

### 4. 登入系統
1. 訪問主頁 `http://localhost:3000/`
2. 使用用戶名和密碼登入
3. 系統會自動保存 JWT token 到 localStorage

### 5. 訪問新頁面
- **聊天頁面**: http://localhost:3000/chat
- **後台管理**: http://localhost:3000/admin

---

## 📋 頁面功能概覽

### 聊天頁面 (`/chat`)

```
┌─────────────────────────────────────┐
│         聊天                         │
├─────┬───────────────────────────────┤
│     │                               │
│對話 │         消息顯示區             │
│列表 │                               │
│     ├───────────────────────────────┤
│     │     消息輸入框 [發送]          │
└─────┴───────────────────────────────┘
```

**功能**:
- ✅ 查看現有對話
- ✅ 創建新對話
- ✅ 發送和接收消息
- ✅ 查看未讀消息數
- ✅ 自動刷新（每 3 秒）

**API 調用**:
```javascript
// 創建對話
POST /api/chat/start
{ "subject": "我的問題" }

// 發送消息
POST /api/chat/send
{ "conversation_id": 1, "message": "Hello" }

// 獲取對話列表
GET /api/chat/conversations

// 獲取對話歷史
GET /api/chat/conversation/1
```

---

### 後台管理 (`/admin`)

```
┌──────────────────────────────────────┐
│          後台管理                     │
├──────┬────────────────────────────────┤
│      │   📊 儀表板                    │
│      │   [用戶管理]                   │
│導航  │   [產品管理]                   │
│菜單  │                               │
│      │   內容動態加載                 │
│      │                               │
└──────┴────────────────────────────────┘
```

**儀表板統計**:
- 📊 總用戶數
- 📦 總產品數
- ⏳ 待審核產品
- 💬 活躍聊天

**用戶管理**:
- 🔍 搜尋用戶
- ✏️ 編輯用戶信息
- 👤 更改用戶角色
- 🗑️ 刪除用戶

**產品管理**:
- 🔍 搜尋產品
- 🏷️ 按狀態篩選
- ✏️ 編輯產品
- ✅ 批准/拒絕
- 🗑️ 刪除產品

**API 調用**:
```javascript
// 獲取統計
GET /api/admin/statistics

// 用戶管理
GET /api/admin/users?search=name&page=1
PUT /api/admin/users/1
DELETE /api/admin/users/1

// 產品管理
GET /api/admin/products?status=pending&page=1
PUT /api/admin/products/1
PUT /api/admin/products/1/approve
PUT /api/admin/products/1/reject
```

---

## 🔐 身份驗證

### Token 儲存
系統使用 JWT token，登入後自動儲存：
```javascript
localStorage.setItem('auth_token', token);
```

### 訪問檢查
所有需要認證的頁面都會自動檢查 token：
```javascript
if (!localStorage.getItem('auth_token')) {
    alert('請先登入');
    window.location.href = '/';
}
```

### 角色檢查
後台管理頁面檢查用戶角色：
```javascript
// 解析 token 獲取用戶信息
const payload = JSON.parse(atob(token.split('.')[1]));
if (payload.role !== 'admin' && payload.role !== 'super_admin') {
    alert('您沒有權限訪問此頁面');
}
```

---

## 🔧 調試技巧

### 1. 檢查 Token
在瀏覽器控制台檢查 token 是否存在：
```javascript
console.log(localStorage.getItem('auth_token'));
```

### 2. 查看 API 請求
打開瀏覽器開發工具 (F12) → Network 選項卡，查看所有 API 請求

### 3. 檢查控制台錯誤
打開 Browser Console (F12) 查看 JavaScript 錯誤

### 4. 檢查後端日誌
查看 Flask 應用的完整錯誤信息

### 5. 測試 API
使用 curl 或 Postman 測試 API：
```bash
# 創建對話
curl -X POST http://localhost:3000/api/chat/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"subject":"Test"}'
```

---

## 📁 文件位置

### 前端文件
```
templates/
├── chat.html          # 聊天 UI
└── admin.html         # 後台管理 UI

static/
├── chat.js            # 聊天邏輯
└── admin.js           # 後台邏輯
```

### 後端文件
```
api/
├── utils/
│   ├── base.py        # 數據庫和基類
│   └── migrations.py   # 數據庫遷移
└── modules/
    ├── user.py        # 用戶認證
    ├── product_search.py
    ├── product_management.py
    ├── upload_history.py
    ├── contact.py
    ├── chat.py        # 聊天 API
    ├── admin.py       # 後台管理 API
    └── pages.py       # 頁面路由
```

### 文檔
```
├── FRONTEND_GUIDE.md  # 前端使用指南
├── ADMIN_PANEL.md     # 後台管理詳細文檔
├── CHAT_FEATURE.md    # 聊天功能詳細文檔
└── API_REFACTORING.md # API 重構說明
```

---

## ⚡ 常見命令

### 啟動應用
```bash
python findconnector_refactored.py
```

### 初始化數據庫
```bash
python -c "from api.utils.migrations import init_all; init_all()"
```

### 進入 Flask Shell
```bash
python -c "from findconnector_refactored import app; app.app_context().push()"
```

### 查看日誌
```bash
tail -f app.log
```

---

## 💡 提示

1. **不要忘記初始化數據庫** - 首次運行必須執行 `init_all()`
2. **檢查瀏覽器控制台** - 出現問題時首先查看控制台錯誤
3. **使用最新瀏覽器** - 確保瀏覽器支持 ES6+
4. **保持 Flask 應用運行** - 前端需要後端 API 支持
5. **複製有效的 token** - 測試時使用真實的 JWT token

---

## 📞 技術支持

如有問題，請檢查：
1. 後端是否正常運行
2. 數據庫是否已初始化
3. 用戶是否已登入（localStorage 中是否有 token）
4. 瀏覽器控制台是否有錯誤信息
5. 後端日誌是否有相關錯誤

---

## 下一步

系統現在已準備完整！您可以：

1. **測試聊天功能** - 訪問 `/chat` 創建對話和發送消息
2. **測試後台管理** - 訪問 `/admin` 管理用戶和產品
3. **添加更多功能** - 根據需要擴展系統
4. **部署到生產** - 配置服務器和 HTTPS

祝您使用愉快！ 🎉
