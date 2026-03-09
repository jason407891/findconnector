# 後台管理功能 (Admin Management) 使用指南

## 概述
新增的管理模組提供了完整的後台管理功能，包括用戶管理和產品管理，支持基於角色的訪問控制（RBAC）。

## 用戶角色系統

### 角色類型

| 角色 | 說明 | 權限 |
|------|------|------|
| `user` | 普通用戶 | 只能管理自己的內容 |
| `admin` | 管理員 | 可以管理用戶和產品（不能删除超級管理員、不能改變用户角色） |
| `super_admin` | 超級管理員 | 完全的系統管理權限 |

## API 端點

### 用戶管理 (User Management)

#### 1. 獲取所有用戶列表
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

#### 2. 獲取特定用戶詳情
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

#### 3. 編輯用戶信息
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

#### 4. 刪除用戶
```
DELETE /api/admin/users/<user_id>
Authorization: <JWT_TOKEN>

限制: 僅super_admin可執行，無法刪除super_admin用戶

回應:
{
    "ok": true
}
```

#### 5. 設置用戶角色
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

### 產品管理 (Product Management)

#### 1. 獲取所有產品列表
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

#### 2. 獲取特定產品詳情
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

#### 3. 編輯產品信息
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

#### 4. 刪除產品
```
DELETE /api/admin/products/<product_id>
Authorization: <JWT_TOKEN>

回應:
{
    "ok": true
}
```

#### 5. 批准/發布產品
```
PUT /api/admin/products/<product_id>/approve
Authorization: <JWT_TOKEN>

回應:
{
    "ok": true
}

效果: 將產品狀態更改為 'published'
```

#### 6. 拒絕產品
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

### 儀表板統計 (Dashboard Statistics)

#### 獲取管理員儀表板統計信息
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

## 數據庫結構

### 用戶表 (users) 新增字段

| 欄位 | 類型 | 說明 |
|------|------|------|
| role | ENUM | 用戶角色: user/admin/super_admin |
| created_at | DATETIME | 創建時間 |
| updated_at | DATETIME | 更新時間 |

### 產品表 (products) 新增字段

| 欄位 | 類型 | 說明 |
|------|------|------|
| status | ENUM | 產品狀態: pending/published/rejected |
| created_at | DATETIME | 創建時間 |

## 初始化

### 執行數據庫遷移
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

### 手動執行 SQL（如果遷移失敗）

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

## 使用場景

### 場景 1：管理員審核用戶
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

### 場景 2：審核產品
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

### 場景 3：編輯產品信息
```
1. 獲取產品列表（可搜尋）
   GET /api/admin/products?search=ABC123

2. 編輯產品
   PUT /api/admin/products/456

3. 檢查統計信息
   GET /api/admin/statistics
```

## 權限檢查

### 自動權限驗證
所有管理端點都會自動檢查用戶是否是 admin 或 super_admin，如果不是會返回 401 錯誤。

### 特殊權限

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

## 錯誤處理

常見的錯誤碼：

```
401 Unauthorized - 無效的 token 或無足夠的權限
403 Forbidden - 用戶權限不足（例如非 super_admin 嘗試删除用戶）
404 Not Found - 資源不存在
400 Bad Request - 請求參數有誤
500 Internal Server Error - 服務器錯誤
```

## 進階功能建議

1. **用戶行為審計日誌** - 記錄所有管理員操作
2. **批量操作** - 支持批量修改用戶或產品
3. **導出報表** - 支持導出用户或產品數據為 CSV
4. **權限模板** - 預定義的權限組合
5. **數據分析** - 更詳細的統計圖表
6. **審批流程** - 多級審批機制
