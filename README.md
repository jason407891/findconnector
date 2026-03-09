# FindConnector - 完整文檔

## 📖 項目概述

**FindConnector** 是一個功能完整的物聯網配件查詢和管理平台，集成了以下功能：
- 🔍 產品搜尋和分類瀏覽
- 👥 用戶認證和管理
- 💬 客服聊天系統
- ⚙️ 後台管理面板

**網站介紹**: https://hackmd.io/@RFiV9dShQruMm3omdjk6sQ/Sk4kg7rgge  
**網站連結**: http://3.104.45.136:3000/

---

## 📚 文檔目錄

1. [快速開始指南](#快速開始指南)
2. [API 重構說明](#api-重構說明)
3. [前端頁面使用指南](#前端頁面使用指南)
4. [聊天功能詳細文檔](#聊天功能詳細文檔)
5. [後台管理功能詳細文檔](#後台管理功能詳細文檔)

---

## 快速開始指南

### 前端頁面已準備完成！

系統現在包含了完整的前端页面供您使用。

### 📱 新增页面

| 頁面 | 路由 | 說明 | 所需角色 |
|------|------|------|--------|
| **聊天** | `/chat` | 與客服溝通 | 任何登入用戶 |
| **後台管理** | `/admin` | 管理用戶和產品 | Admin / Super Admin |

---

### 🚀 快速開始步驟

#### 1. 確保後端已啟動
```bash
python findconnector_refactored.py
```

應該看到類似的輸出：
```
 * Running on http://127.0.0.1:3000
```

#### 2. 初始化數據庫
在 Python 命令行中執行：
```python
from api.utils.migrations import init_all
init_all()
```

如果你看到「All migrations completed successfully!」表示成功。

#### 3. 創建測試用戶

通過後端 API 或數據庫直接創建用戶：

```mysql
-- 創建普通用戶
INSERT INTO users (username, email, password_hash, company, role)
VALUES ('testuser', 'test@example.com', 'hashed_password', 'Test Company', 'user');

-- 創建管理員用戶
INSERT INTO users (username, email, password_hash, company, role)
VALUES ('admin', 'admin@example.com', 'hashed_password', 'Admin Company', 'admin');
```

#### 4. 登入系統
1. 訪問主頁 `http://localhost:3000/`
2. 使用用戶名和密碼登入
3. 系統會自動保存 JWT token 到 localStorage

#### 5. 訪問新頁面
- **聊天頁面**: http://localhost:3000/chat
- **後台管理**: http://localhost:3000/admin

---

### 📋 頁面功能概覽

#### 聊天頁面 (`/chat`)

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

#### 後台管理 (`/admin`)

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

### 🔐 身份驗證

#### Token 儲存
系統使用 JWT token，登入後自動儲存：
```javascript
localStorage.setItem('auth_token', token);
```

#### 訪問檢查
所有需要認證的頁面都會自動檢查 token：
```javascript
if (!localStorage.getItem('auth_token')) {
    alert('請先登入');
    window.location.href = '/';
}
```

#### 角色檢查
後台管理頁面檢查用戶角色：
```javascript
// 解析 token 獲取用戶信息
const payload = JSON.parse(atob(token.split('.')[1]));
if (payload.role !== 'admin' && payload.role !== 'super_admin') {
    alert('您沒有權限訪問此頁面');
}
```

---

### 🔧 調試技巧

#### 1. 檢查 Token
在瀏覽器控制台檢查 token 是否存在：
```javascript
console.log(localStorage.getItem('auth_token'));
```

#### 2. 查看 API 請求
打開瀏覽器開發工具 (F12) → Network 選項卡，查看所有 API 請求

#### 3. 檢查控制台錯誤
打開 Browser Console (F12) 查看 JavaScript 錯誤

#### 4. 檢查後端日誌
查看 Flask 應用的完整錯誤信息

#### 5. 測試 API
使用 curl 或 Postman 測試 API：
```bash
# 創建對話
curl -X POST http://localhost:3000/api/chat/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"subject":"Test"}'
```

---

### 📁 文件位置

#### 前端文件
```
templates/
├── chat.html          # 聊天 UI
└── admin.html         # 後台管理 UI

static/
├── chat.js            # 聊天邏輯
└── admin.js           # 後台邏輯
```

#### 後端文件
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

---

### ⚡ 常見命令

#### 啟動應用
```bash
python findconnector_refactored.py
```

#### 初始化數據庫
```bash
python -c "from api.utils.migrations import init_all; init_all()"
```

#### 進入 Flask Shell
```bash
python -c "from findconnector_refactored import app; app.app_context().push()"
```

#### 查看日誌
```bash
tail -f app.log
```

---

### 💡 提示

1. **不要忘記初始化數據庫** - 首次運行必須執行 `init_all()`
2. **檢查瀏覽器控制台** - 出現問題時首先查看控制台錯誤
3. **使用最新瀏覽器** - 確保瀏覽器支持 ES6+
4. **保持 Flask 應用運行** - 前端需要後端 API 支持
5. **複製有效的 token** - 測試時使用真實的 JWT token

---

### 📞 技術支持

如有問題，請檢查：
1. 後端是否正常運行
2. 數據庫是否已初始化
3. 用戶是否已登入（localStorage 中是否有 token）
4. 瀏覽器控制台是否有錯誤信息
5. 後端日誌是否有相關錯誤

---

## API 重構說明

### 概述
原始的 `findconnector.py` 已經用面向對象的設計重構，將不同功能的 API 分離成獨立的類別，並組織在 `utils` 和 `modules` 中。

### 新的文件結構

```
findconnector/
├── api/
│   ├── __init__.py                      # API 模組說明
│   ├── utils/                           # 通用工具
│   │   ├── __init__.py
│   │   └── base.py                      # BaseAPI、DatabaseManager
│   └── modules/                         # 業務邏輯模組
│       ├── __init__.py
│       ├── category.py                  # 產品類別和製造商 API
│       ├── user.py                      # 用戶註冊和認證 API
│       ├── product_search.py            # 產品搜尋 API
│       ├── product_management.py        # 產品上傳、編輯、刪除 API
│       ├── upload_history.py            # 上傳歷史和批量上傳 API
│       ├── contact.py                   # 聯絡反饋 API
│       ├── chat.py                      # 聊天功能 API
│       ├── admin.py                     # 後台管理 API
│       └── pages.py                     # 頁面路由
├── findconnector_refactored.py          # 新的主應用檔案
├── findconnector.py                     # 原始檔案 (保留以備參考)
└── README.md
```

### 目錄劃分說明

#### utils/ 目錄 - 通用工具
包含所有跨模組使用的基礎類別和工具：
- **base.py**
  - `DatabaseManager`: 單例模式的數據庫連接池管理
  - `BaseAPI`: 所有 API 類別的基類，提供通用的數據庫操作方法

#### modules/ 目錄 - 業務邏輯模組
按功能領域組織的 API 模組：

##### 1. category.py - 產品分類
- `CategoryAPI.get_categories()` - 獲取所有產品類別
- `CategoryAPI.get_manufacturers()` - 獲取所有製造商/品牌

##### 2. user.py - 用戶管理
- `UserAPI.register()` - 用戶註冊
- `UserAPI.login()` - 用戶登入（返回JWT token）
- `UserAPI.verify_token()` - 驗證JWT token
- `UserAPI.get_user_from_token()` - 靜態方法，從token提取用戶信息

##### 3. product_search.py - 產品搜尋
- `ProductSearchAPI.search_products()` - 按部件號搜尋產品（支持分頁）

##### 4. product_management.py - 產品管理
- `ProductManagementAPI.upload_single_product()` - 上傳單個產品
- `ProductManagementAPI.edit_product()` - 編輯產品信息
- `ProductManagementAPI.delete_product()` - 刪除產品

##### 5. upload_history.py - 上傳歷史
- `UploadHistoryAPI.get_upload_history()` - 獲取用戶的上傳歷史
- `UploadHistoryAPI.batch_upload()` - 批量上傳產品（從Excel文件）

##### 6. contact.py - 客戶反饋
- `ContactAPI.send_message()` - 通過Discord webhook發送反饋消息

##### 7. chat.py - 聊天功能
- 完整的對話和消息管理系統

##### 8. admin.py - 後台管理
- 用戶和產品管理功能，支持 RBAC

##### 9. pages.py - 頁面路由
- `PageAPI` 中的靜態方法，負責所有 HTML 頁面渲染

### 升級指南

#### 選項 1: 逐步遷移
如果要逐步遷移，可以保留原始的 `findconnector.py`，同時引入新的 API 類別：

```python
from api.modules import CategoryAPI, UserAPI
# ... 等等

category_api = CategoryAPI()
user_api = UserAPI()
```

#### 選項 2: 完全替換
如果要完全使用新的結構，使用 `findconnector_refactored.py` 作為主應用檔案：

```bash
# 備份原始文件
cp findconnector.py findconnector_backup.py

# 使用新的應用文件
mv findconnector_refactored.py findconnector.py
```

### 優點

1. **代碼組織** - 相關功能被有邏輯地組織在 utils 和 modules 中
2. **可維護性** - 更容易找到和修改特定功能
3. **可測試性** - 每個類別可以獨立測試
4. **代碼重用** - 通用功能在 BaseAPI 和工具類中定義
5. **單一責任** - 每個模組只負責一個功能域
6. **層級清晰** - utils 層提供基礎設施，modules 層提供業務邏輯

### 依賴項

確保已安裝所有需要的依賴項：
```bash
pip install flask
pip install PyJWT
pip install requests
pip install pandas
pip install openpyxl  # for Excel file support
pip install mysql-connector-python
pip install python-dotenv
```

### 環境變量

確保 `.env` 檔案包含以下變量：
```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
secret_key=your_secret_key
dc_url=your_discord_webhook_url
```

### 路由對應

| 路由 | 方法 | 類別 | 功能 |
|------|------|------|------|
| `/api/showcategories` | GET | CategoryAPI | 獲取分類 |
| `/api/manufacturer` | GET | CategoryAPI | 獲取製造商 |
| `/api/user` | POST | UserAPI | 用戶註冊 |
| `/api/user/auth` | PUT/GET | UserAPI | 登入/驗證 |
| `/api/search/<product>` | GET | ProductSearchAPI | 搜尋產品 |
| `/api/uploadone` | POST | ProductManagementAPI | 上傳單個產品 |
| `/api/editproduct` | PUT | ProductManagementAPI | 編輯產品 |
| `/api/deleteproduct` | DELETE | ProductManagementAPI | 刪除產品 |
| `/api/uploadhistory` | GET | UploadHistoryAPI | 上傳歷史 |
| `/api/batchupload` | POST | UploadHistoryAPI | 批量上傳 |
| `/api/contact` | POST | ContactAPI | 發送反饋 |
| `/api/chat/*` | * | ChatAPI | 聊天功能 |
| `/api/admin/*` | * | AdminAPI | 後台管理 |

### 注意事項

- 所有需要身份驗證的 API 端點都使用 JWT token（Authorization header）
- 數據庫連接使用單例模式的連接池，確保效率
- 所有 API 響應都遵循統一的 JSON 格式

---

## 前端頁面使用指南

### 概述
已為聊天功能和後台管理系統創建了完整的前端 HTML 和 JavaScript。

### 頁面清單

#### 1. 聊天頁面 (Chat Page)
**文件**: 
- HTML: `templates/chat.html`
- JavaScript: `static/chat.js`

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

#### 2. 後台管理頁面 (Admin Panel)
**文件**:
- HTML: `templates/admin.html`
- JavaScript: `static/admin.js`

**訪問路由**: `GET /admin`

**功能**:

##### 儀表板 (Dashboard)
- 📊 顯示關鍵統計數據：
  - 總用戶數
  - 總產品數
  - 待審核產品數
  - 活躍聊天數

##### 用戶管理 (User Management)
- 🔍 搜尋用戶（按用戶名或郵箱）
- 📋 列表顯示所有用戶
- ✏️ 編輯用戶信息（用戶名、公司、電話、地址、角色）
- 🗑️ 刪除用戶
- 📄 分頁支持

##### 產品管理 (Product Management)
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

### 技術堆棧

#### 前端技術
- **HTML5** - 語義化標記
- **CSS3** - 響應式設計、Flexbox、Grid
- **Vanilla JavaScript** - 無框架依賴，純 JavaScript
- **Fetch API** - 與後端通訊

#### 特性
- ✅ 完全響應式設計（支持手機、平板、桌面）
- ✅ 無第三方依賴（除了 Flask 後端）
- ✅ 實時數據更新
- ✅ 優雅的錯誤處理
- ✅ 本地存儲 JWT token

### 樣式和 UI/UX

#### 聊天頁面
- 左側欄：對話列表
- 右側：消息顯示區和輸入框
- 消息氣泡：不同顏色區分用戶和客服
- 響應式：手機上堆疊布局

#### 後台管理
- 左側邊欄：導航菜單
- 主要內容區：動態內容面板
- 統計卡片：網格布局
- 表格：可排序的數據展示
- 模態框：編輯和操作窗口

### 環境要求

#### 後端要求
1. Flask 應用必須運行在 `/` 根路由
2. 所有 API 端點必須在 `/api` 路由下
3. JWT token 需要在 Authorization header 中傳遞

#### 前端要求
1. 現代瀏覽器支持 ES6+ JavaScript
2. LocalStorage 用於存儲 token
3. Fetch API 支持

### 常見問題

#### Q: 頁面顯示 "請先登入"
A: 需要先在主頁登入並獲取 JWT token，token 會自動保存到 localStorage

#### Q: 消息沒有實時更新
A: 頁面會每 3 秒自動刷新一次消息，如需實時推送建議使用 WebSocket

#### Q: 無法訪問後台管理
A: 用戶必須具有 admin 或 super_admin 角色，普通 user 角色無法訪問

#### Q: 編輯後數據沒有改變
A: 檢查後端 API 是否返回成功響應，查看瀏覽器控制台的錯誤信息

### 進階功能建議

#### 聊天功能
1. **WebSocket 實時通訊** - 使用 WebSocket 實現即時消息推送
2. **文件上傳** - 支持上傳圖片或文件
3. **Markdown 支持** - 支持 Markdown 格式的消息
4. **搜尋功能** - 搜尋歷史消息
5. **消息已讀狀態** - 顯示消息是否被客服閱讀

#### 後台管理
1. **高級搜尋** - 多條件組合搜尋
2. **批量操作** - 批量刪除或更新
3. **導出功能** - 導出數據為 CSV/Excel
4. **圖表分析** - 使用 Chart.js 顯示統計圖表
5. **操作日誌** - 審計管理員操作記錄
6. **權限管理** - 更細粒度的權限控制

### 部署建議

#### 開發環境
```bash
python findconnector_refactored.py
# 訪問 http://localhost:3000/chat 或 http://localhost:3000/admin
```

#### 生產環境
1. 使用 Gunicorn 或其他 WSGI 服務器
2. 啟用 HTTPS
3. 設置適當的 CORS 策略
4. 配置靜態文件伺服
5. 使用 CDN 加速

---

## 聊天功能詳細文檔

### 概述
新增的聊天模組提供了用戶與客服之間的實時對話功能，包括消息存儲、對話歷史和未讀消息管理。

### 功能特性

#### 1. 對話管理
- **創建對話**: 用戶可以與客服開始新的對話
- **多個對話**: 用戶可以同時進行多個對話
- **對話狀態**: 支持 open（開放）、closed（已關閉）、waiting（等待中）三種狀態

#### 2. 消息功能
- **發送消息**: 用戶和客服都可以發送消息
- **消息類型區分**: user（用戶消息）、agent（客服消息）
- **已讀追蹤**: 自動追蹤消息是否已讀
- **時間戳記**: 每條消息都記錄發送時間

#### 3. 通知管理
- **未讀計數**: 獲取未讀消息數量
- **自動標記**: 查看對話時自動將消息標記為已讀

### API 端點

#### 1. 創建新對話
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

#### 2. 發送消息
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

#### 3. 獲取所有對話列表
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

#### 4. 獲取對話歷史
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

#### 5. 標記對話為已讀
```
PUT /api/chat/conversation/1/read
Authorization: <JWT_TOKEN>

回應:
{
    "ok": true
}
```

#### 6. 獲取未讀消息計數
```
GET /api/chat/unread
Authorization: <JWT_TOKEN>

回應:
{
    "unread_count": 3
}
```

### 數據庫結構

#### conversations 表
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

#### chat_messages 表
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | INT | 主鍵 |
| conversation_id | INT | 對話ID |
| user_id | INT | 用戶ID |
| message | LONGTEXT | 消息內容 |
| message_type | ENUM | user/agent |
| is_read | BOOLEAN | 是否已讀 |
| created_at | DATETIME | 創建時間 |

### 初始化

#### 方式 1：使用遷移腳本
```python
from api.utils.migrations import init_chat_tables

init_chat_tables()
```

#### 方式 2：手動執行 SQL
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

### 使用場景

#### 場景 1：用戶發起對話
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

#### 場景 2：查看對話歷史
```python
# 1. 獲取對話列表
GET /api/chat/conversations

# 2. 點擊對話後，獲取歷史記錄
GET /api/chat/conversation/1

# 3. 自動標記為已讀
# (會在獲取歷史時自動執行)
```

#### 場景 3：監控未讀消息
```python
# 定期檢查是否有新消息
GET /api/chat/unread

# 如果 unread_count > 0，提示用戶有新消息
```

### 進階功能建議

1. **即時通知** - 使用 WebSocket 實現實時消息推送
2. **文件上傳** - 支持在聊天中上傳圖片或文件
3. **客服端面板** - 建立客服管理後台以回復消息
4. **自動回復** - 設置自動回復規則（如下班時間提示）
5. **消息搜索** - 支持搜索歷史消息
6. **批量操作** - 支持批量關閉對話或轉移客服

### 注意事項

- 所有 API 端點都需要有效的 JWT token（除了用戶註冊和登入）
- 用戶只能看到自己的對話
- 消息自動按時間順序排列
- 客服消息自動標記為已讀（首次查看時）

---

## 後台管理功能詳細文檔

### 概述
新增的管理模組提供了完整的後台管理功能，包括用戶管理和產品管理，支持基於角色的訪問控制（RBAC）。

### 用戶角色系統

#### 角色類型

| 角色 | 說明 | 權限 |
|------|------|------|
| `user` | 普通用戶 | 只能管理自己的內容 |
| `admin` | 管理員 | 可以管理用戶和產品（不能删除超級管理員、不能改變用户角色） |
| `super_admin` | 超級管理員 | 完全的系統管理權限 |

### API 端點

#### 用戶管理 (User Management)

##### 1. 獲取所有用戶列表
```
GET /api/admin/users?page=1&search=&role=
Authorization: <JWT_TOKEN>

參數:
- page: 頁碼（默認1）
- search: 按姓名或郵箱搜尋（可選）
- role: 按角色篩選 (user/admin/super_admin)（可選）

回應:
{
    "users": [
        {
            "id": 1,
            "user_name": "John Doe",
            "user_email": "john@example.com",
            "company_name": "ABC Corp",
            "phone_number": "123456789",
            "warehouse_address": "123 Main St",
            "role": "admin",
            "created_at": "2024-03-09 10:00:00",
            "updated_at": "2024-03-09 14:00:00"
        }
    ],
    "page": 1,
    "total": 50,
    "pages": 3
}
```

##### 2. 獲取特定用戶詳情
```
GET /api/admin/users/<user_id>
Authorization: <JWT_TOKEN>

回應:
{
    "id": 1,
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "company_name": "ABC Corp",
    "phone_number": "123456789",
    "warehouse_address": "123 Main St",
    "role": "admin",
    "created_at": "2024-03-09 10:00:00",
    "updated_at": "2024-03-09 14:00:00"
}
```

##### 3. 編輯用戶信息
```
PUT /api/admin/users/<user_id>
Authorization: <JWT_TOKEN>
Content-Type: application/json

{
    "user_name": "Jane Doe",
    "company_name": "XYZ Corp",
    "phone_number": "987654321",
    "warehouse_address": "456 Oak Ave",
    "role": "admin" (僅super_admin可修改)
}

回應:
{
    "ok": true
}
```

##### 4. 刪除用戶
```
DELETE /api/admin/users/<user_id>
Authorization: <JWT_TOKEN>

限制: 僅super_admin可執行，無法刪除super_admin用戶

回應:
{
    "ok": true
}
```

##### 5. 設置用戶角色
```
PUT /api/admin/users/<user_id>/role
Authorization: <JWT_TOKEN>
Content-Type: application/json

{
    "role": "admin"  // 可選值: user, admin, super_admin
}

限制: 僅super_admin可執行

回應:
{
    "ok": true
}
```

#### 產品管理 (Product Management)

##### 1. 獲取所有產品列表
```
GET /api/admin/products?page=1&search=&status=&category=
Authorization: <JWT_TOKEN>

參數:
- page: 頁碼（默認1）
- search: 按部件號、產品名稱或品牌搜尋（可選）
- status: 按狀態篩選 (pending/published/rejected)（可選）
- category: 按分類篩選（可選）

回應:
{
    "products": [
        {
            "id": 1,
            "upload_user": "user@example.com",
            "partnumber": "ABC123",
            "brand": "XYZ",
            "qty": 100,
            "price": 99.99,
            "category": "Electronics",
            "status": "published",
            "product_img": "https://...",
            "update_time": "2024-03-09 14:00:00",
            "created_at": "2024-03-09 10:00:00"
        }
    ],
    "page": 1,
    "total": 200,
    "pages": 10
}
```

##### 2. 獲取特定產品詳情
```
GET /api/admin/products/<product_id>
Authorization: <JWT_TOKEN>

回應:
{
    "id": 1,
    "upload_user": "user@example.com",
    "partnumber": "ABC123",
    "brand": "XYZ",
    "qty": 100,
    "price": 99.99,
    "category": "Electronics",
    "dc": "2024-03",
    "description": "Product description",
    "status": "published",
    "product_img": "https://...",
    "update_time": "2024-03-09 14:00:00",
    "created_at": "2024-03-09 10:00:00"
}
```

##### 3. 編輯產品信息
```
PUT /api/admin/products/<product_id>
Authorization: <JWT_TOKEN>
Content-Type: application/json

{
    "brand": "New Brand",
    "qty": 150,
    "price": 89.99,
    "category": "Electronics",
    "description": "Updated description",
    "status": "published"
}

回應:
{
    "ok": true
}
```

##### 4. 刪除產品
```
DELETE /api/admin/products/<product_id>
Authorization: <JWT_TOKEN>

回應:
{
    "ok": true
}
```

##### 5. 批准/發布產品
```
PUT /api/admin/products/<product_id>/approve
Authorization: <JWT_TOKEN>

回應:
{
    "ok": true
}

效果: 將產品狀態更改為 'published'
```

##### 6. 拒絕產品
```
PUT /api/admin/products/<product_id>/reject
Authorization: <JWT_TOKEN>
Content-Type: application/json

{
    "reason": "產品不符合要求"（可選）
}

回應:
{
    "ok": true
}

效果: 將產品狀態更改為 'rejected'
```

#### 儀表板統計 (Dashboard Statistics)

##### 獲取管理員儀表板統計信息
```
GET /api/admin/statistics
Authorization: <JWT_TOKEN>

回應:
{
    "total_users": 150,
    "total_products": 500,
    "pending_products": 5,
    "active_chats": 12
}
```

### 數據庫結構

#### 用戶表 (users) 新增字段

| 欄位 | 類型 | 說明 |
|------|------|------|
| role | ENUM | 用戶角色: user/admin/super_admin |
| created_at | DATETIME | 創建時間 |
| updated_at | DATETIME | 更新時間 |

#### 產品表 (products) 新增字段

| 欄位 | 類型 | 說明 |
|------|------|------|
| status | ENUM | 產品狀態: pending/published/rejected |
| created_at | DATETIME | 創建時間 |

### 初始化

#### 執行數據庫遷移
```python
from api.utils.migrations import init_all

# 初始化所有表
init_all()
```

或者單獨執行：
```python
from api.utils.migrations import add_role_to_users, add_status_to_products

add_role_to_users()      # 添加用戶角色字段
add_status_to_products() # 添加產品狀態字段
```

#### 手動執行 SQL（如果遷移失敗）

```sql
-- 為 users 表添加角色
ALTER TABLE users 
ADD COLUMN role ENUM('user', 'admin', 'super_admin') DEFAULT 'user',
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD INDEX idx_role (role);

-- 為 products 表添加狀態
ALTER TABLE products 
ADD COLUMN status ENUM('pending', 'published', 'rejected') DEFAULT 'published',
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD INDEX idx_status (status),
ADD INDEX idx_created_at (created_at);
```

### 使用場景

#### 場景 1：管理員審核用戶
```
1. 獲取所有用戶列表
   GET /api/admin/users

2. 查看特定用戶詳情
   GET /api/admin/users/123

3. 編輯用户信息或設置角色
   PUT /api/admin/users/123
   或
   PUT /api/admin/users/123/role
```

#### 場景 2：審核產品
```
1. 獲取所有待審核產品
   GET /api/admin/products?status=pending

2. 查看產品詳情
   GET /api/admin/products/456

3. 批准或拒絕產品
   PUT /api/admin/products/456/approve
   或
   PUT /api/admin/products/456/reject
```

#### 場景 3：編輯產品信息
```
1. 獲取產品列表（可搜尋）
   GET /api/admin/products?search=ABC123

2. 編輯產品
   PUT /api/admin/products/456

3. 檢查統計信息
   GET /api/admin/statistics
```

### 權限檢查

#### 自動權限驗證
所有管理端點都會自動檢查用戶是否是 admin 或 super_admin，如果不是會返回 401 錯誤。

#### 特殊權限

| 操作 | 最低權限 | 說明 |
|------|---------|------|
| 查看用戶列表 | admin | - |
| 查看用戶詳情 | admin | - |
| 編輯用戶 | admin | 編輯角色需要 super_admin |
| 刪除用戶 | super_admin | 無法删除 super_admin 用戶 |
| 修改用戶角色 | super_admin | - |
| 查看產品列表 | admin | - |
| 查看產品詳情 | admin | - |
| 編輯產品 | admin | - |
| 刪除產品 | admin | - |
| 批准產品 | admin | - |
| 拒絕產品 | admin | - |
| 查看統計信息 | admin | - |

### 錯誤處理

常見的錯誤碼：

```
401 Unauthorized - 無效的 token 或無足夠的權限
403 Forbidden - 用戶權限不足（例如非 super_admin 嘗試删除用戶）
404 Not Found - 資源不存在
400 Bad Request - 請求參數有誤
500 Internal Server Error - 服務器錯誤
```

### 進階功能建議

1. **用戶行為審計日誌** - 記錄所有管理員操作
2. **批量操作** - 支持批量修改用戶或產品
3. **導出報表** - 支持導出用户或產品數據為 CSV
4. **權限模板** - 預定義的權限組合
5. **數據分析** - 更詳細的統計圖表
6. **審批流程** - 多級審批機制

---

## 下一步

系統現在已準備完整！您可以：

1. **測試聊天功能** - 訪問 `/chat` 創建對話和發送消息
2. **測試後台管理** - 訪問 `/admin` 管理用戶和產品
3. **添加更多功能** - 根據需要擴展系統
4. **部署到生產** - 配置服務器和 HTTPS

祝您使用愉快！ 🎉
