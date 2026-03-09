# Flask API 重構指南

## 概述
原始的 `findconnector.py` 已經用面向對象的設計重構，將不同功能的 API 分離成獨立的類別，並組織在 `utils` 和 `modules` 中。

## 新的文件結構

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
│       └── pages.py                     # 頁面路由
├── findconnector_refactored.py          # 新的主應用檔案
├── findconnector.py                     # 原始檔案 (保留以備參考)
└── README.md
```

## 目錄劃分說明

### utils/ 目錄 - 通用工具
包含所有跨模組使用的基礎類別和工具：
- **base.py**
  - `DatabaseManager`: 單例模式的數據庫連接池管理
  - `BaseAPI`: 所有 API 類別的基類，提供通用的數據庫操作方法

### modules/ 目錄 - 業務邏輯模組
按功能領域組織的 API 模組：

#### 1. category.py - 產品分類
- `CategoryAPI.get_categories()` - 獲取所有產品類別
- `CategoryAPI.get_manufacturers()` - 獲取所有製造商/品牌

#### 2. user.py - 用戶管理
- `UserAPI.register()` - 用戶註冊
- `UserAPI.login()` - 用戶登入（返回JWT token）
- `UserAPI.verify_token()` - 驗證JWT token
- `UserAPI.get_user_from_token()` - 靜態方法，從token提取用戶信息

#### 3. product_search.py - 產品搜尋
- `ProductSearchAPI.search_products()` - 按部件號搜尋產品（支持分頁）

#### 4. product_management.py - 產品管理
- `ProductManagementAPI.upload_single_product()` - 上傳單個產品
- `ProductManagementAPI.edit_product()` - 編輯產品信息
- `ProductManagementAPI.delete_product()` - 刪除產品

#### 5. upload_history.py - 上傳歷史
- `UploadHistoryAPI.get_upload_history()` - 獲取用戶的上傳歷史
- `UploadHistoryAPI.batch_upload()` - 批量上傳產品（從Excel文件）

#### 6. contact.py - 客戶反饋
- `ContactAPI.send_message()` - 通過Discord webhook發送反饋消息

#### 7. pages.py - 頁面路由
- `PageAPI` 中的靜態方法，負責所有 HTML 頁面渲染

## 升級指南

### 選項 1: 逐步遷移
如果要逐步遷移，可以保留原始的 `findconnector.py`，同時引入新的 API 類別：

```python
from api.modules import CategoryAPI, UserAPI
# ... 等等

category_api = CategoryAPI()
user_api = UserAPI()
```

### 選項 2: 完全替換
如果要完全使用新的結構，使用 `findconnector_refactored.py` 作為主應用檔案：

```bash
# 備份原始文件
cp findconnector.py findconnector_backup.py

# 使用新的應用文件
mv findconnector_refactored.py findconnector.py
```

## 優點

1. **代碼組織** - 相關功能被有邏輯地組織在 utils 和 modules 中
2. **可維護性** - 更容易找到和修改特定功能
3. **可測試性** - 每個類別可以獨立測試
4. **代碼重用** - 通用功能在 BaseAPI 和工具類中定義
5. **單一責任** - 每個模組只負責一個功能域
6. **層級清晰** - utils 層提供基礎設施，modules 層提供業務邏輯

## 依賴項

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

## 環境變量

確保 `.env` 檔案包含以下變量：
```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
secret_key=your_secret_key
dc_url=your_discord_webhook_url
```

## 路由對應

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

## 注意事項

- 所有需要身份驗證的 API 端點都使用 JWT token（Authorization header）
- 數據庫連接使用單例模式的連接池，確保效率
- 所有 API 響應都遵循統一的 JSON 格式
