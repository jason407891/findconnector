# 前端頁面使用指南

## 概述
已為聊天功能和後台管理系統創建了完整的前端 HTML 和 JavaScript。

## 頁面清單

### 1. 聊天頁面 (Chat Page)
**文件**: 
- HTML: [templates/chat.html](templates/chat.html)
- JavaScript: [static/chat.js](static/chat.js)

**訪問路由**: `GET /chat`

**功能**:
- ✅ 對話列表（側邊欄）
- ✅ 實時消息顯示
- ✅ 發送消息功能
- ✅ 未讀消息計數
- ✅ 自動刷新消息（每3秒）
- ✅ 創建新對話
- ✅ 對話歷史查看

**使用步驟**:
1. 用戶需要先登入（JWT token 存儲在 localStorage）
2. 訪問 `/chat` 頁面
3. 可以選擇現有對話或點擊「新增對話」創建新對話
4. 在輸入框中輸入消息，按 Enter 或點擊「發送」按鈕發送
5. 消息會實時顯示，未讀消息會在頁面標題中顯示計數

**後端 API 依賴**:
- `POST /api/chat/start` - 創建對話
- `POST /api/chat/send` - 發送消息
- `GET /api/chat/conversations` - 獲取對話列表
- `GET /api/chat/conversation/<id>` - 獲取對話歷史
- `GET /api/chat/unread` - 獲取未讀計數

---

### 2. 後台管理頁面 (Admin Panel)
**文件**:
- HTML: [templates/admin.html](templates/admin.html)
- JavaScript: [static/admin.js](static/admin.js)

**訪問路由**: `GET /admin`

**功能**:

#### 儀表板 (Dashboard)
- 📊 顯示關鍵統計數據：
  - 總用戶數
  - 總產品數
  - 待審核產品數
  - 活躍聊天數

#### 用戶管理 (User Management)
- 🔍 搜尋用戶（按用戶名或郵箱）
- 📋 列表顯示所有用戶
- ✏️ 編輯用戶信息（用戶名、公司、電話、地址、角色）
- 🗑️ 刪除用戶
- 📄 分頁支持

#### 產品管理 (Product Management)
- 🔍 搜尋產品（按部件號）
- 🏷️ 按狀態篩選（已發布、待審核、已拒絕）
- 📋 列表顯示所有產品
- ✏️ 編輯產品信息（品牌、數量、價格、分類、描述）
- ✅ 批准/發布產品（待審核狀態）
- ❌ 拒絕產品（待審核狀態）
- 🗑️ 刪除產品
- 📄 分頁支持

**使用步驟**:
1. 用戶需要是 admin 或 super_admin 角色
2. 訪問 `/admin` 頁面
3. 選擇要管理的功能（儀表板、用戶或產品）
4. 在側邊欄菜單中切換面板
5. 可以搜尋、篩選、編輯或刪除項目

**後端 API 依賴**:
- `GET /api/admin/statistics` - 獲取統計數據
- `GET /api/admin/users` - 獲取用戶列表
- `GET /api/admin/users/<id>` - 獲取用戶詳情
- `PUT /api/admin/users/<id>` - 編輯用戶
- `DELETE /api/admin/users/<id>` - 刪除用戶
- `GET /api/admin/products` - 獲取產品列表
- `GET /api/admin/products/<id>` - 獲取產品詳情
- `PUT /api/admin/products/<id>` - 編輯產品
- `DELETE /api/admin/products/<id>` - 刪除產品
- `PUT /api/admin/products/<id>/approve` - 批准產品
- `PUT /api/admin/products/<id>/reject` - 拒絕產品

---

## 技術堆棧

### 前端技術
- **HTML5** - 語義化標記
- **CSS3** - 響應式設計、Flexbox、Grid
- **Vanilla JavaScript** - 無框架依賴，純 JavaScript
- **Fetch API** - 與後端通訊

### 特性
- ✅ 完全響應式設計（支持手機、平板、桌面）
- ✅ 無第三方依賴（除了 Flask 後端）
- ✅ 實時數據更新
- ✅ 優雅的錯誤處理
- ✅ 本地存儲 JWT token

---

## 身份驗證

所有頁面都需要有效的 JWT token：

```javascript
// token 存儲位置
localStorage.setItem('auth_token', token);

// 自動檢查登入狀態
if (!localStorage.getItem('auth_token')) {
    alert('請先登入');
    window.location.href = '/';
}
```

---

## 樣式和 UI/UX

### 聊天頁面
- 左側欄：對話列表
- 右側：消息顯示區和輸入框
- 消息氣泡：不同顏色區分用戶和客服
- 響應式：手機上堆疊布局

### 後台管理
- 左側邊欄：導航菜單
- 主要內容區：動態內容面板
- 統計卡片：網格布局
- 表格：可排序的數據展示
- 模態框：編輯和操作窗口

---

## 文件結構

```
templates/
├── chat.html           # 聊天頁面
└── admin.html          # 後台管理頁面

static/
├── chat.js             # 聊天功能 JavaScript
└── admin.js            # 後台管理 JavaScript
```

---

## 環境要求

### 後端要求
1. Flask 應用必須運行在 `/` 根路由
2. 所有 API 端點必須在 `/api` 路由下
3. JWT token 需要在 Authorization header 中傳遞

### 前端要求
1. 現代瀏覽器支持 ES6+ JavaScript
2. LocalStorage 用於存儲 token
3. Fetch API 支持

---

## 常見問題

### Q: 頁面顯示 "請先登入"
A: 需要先在主頁登入並獲取 JWT token，token 會自動保存到 localStorage

### Q: 消息沒有實時更新
A: 頁面會每 3 秒自動刷新一次消息，如需實時推送建議使用 WebSocket

### Q: 無法訪問後台管理
A: 用戶必須具有 admin 或 super_admin 角色，普通 user 角色無法訪問

### Q: 編輯後數據沒有改變
A: 檢查後端 API 是否返回成功響應，查看瀏覽器控制台的錯誤信息

---

## 進階功能建議

### 聊天功能
1. **WebSocket 實時通訊** - 使用 WebSocket 實現即時消息推送
2. **文件上傳** - 支持上傳圖片或文件
3. **Markdown 支持** - 支持 Markdown 格式的消息
4. **搜尋功能** - 搜尋歷史消息
5. **消息已讀狀態** - 顯示消息是否被客服閱讀

### 後台管理
1. **高級搜尋** - 多條件組合搜尋
2. **批量操作** - 批量刪除或更新
3. **導出功能** - 導出數據為 CSV/Excel
4. **圖表分析** - 使用 Chart.js 顯示統計圖表
5. **操作日誌** - 審計管理員操作記錄
6. **權限管理** - 更細粒度的權限控制

---

## 部署建議

### 開發環境
```bash
python findconnector_refactored.py
# 訪問 http://localhost:3000/chat 或 http://localhost:3000/admin
```

### 生產環境
1. 使用 Gunicorn 或其他 WSGI 服務器
2. 啟用 HTTPS
3. 設置適當的 CORS 策略
4. 配置靜態文件伺服
5. 使用 CDN 加速

---

## 許可證和支持

如有任何問題或建議，請參考相關的 API 文檔：
- [CHAT_FEATURE.md](CHAT_FEATURE.md) - 聊天 API 詳細文檔
- [ADMIN_PANEL.md](ADMIN_PANEL.md) - 後台管理 API 詳細文檔
