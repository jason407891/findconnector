# 階梯價格功能實現指南

## 📋 概述

系統實現了完整的階梯價格功能，允許為不同的採購數量設置不同的單價。

**支持格式：**
```json
[
  {"quantity": 1, "price": 150},
  {"quantity": 5, "price": 145},
  {"quantity": 10, "price": 140}
]
```

---

## 🗄️ 數據庫遷移

### SQL 命令

將 `price` 列從數值類型改為 JSON 類型：

```sql
ALTER TABLE products 
MODIFY COLUMN price JSON COMMENT 'JSON array of tiered pricing: [{"quantity": N, "price": X}, ...]';
```

### 自動遷移

系統包含自動遷移函數，可將現有的單一價格自動轉換為階梯格式：

```python
from api.utils.migrations import convert_price_to_json
convert_price_to_json()
```

或在項目啟動時執行所有遷移：

```python
from api.utils.migrations import init_all
init_all()
```

**轉換規則：**
- 舊值 `100` → 新值 `[{"quantity": 1, "price": 100}]`

---

## 🎯 前端用法

### 1. 單筆上傳

**URL:** `POST /api/upload`

#### 方式A：單一價格

```javascript
const formData = new FormData();
formData.append('brand', 'MOLEX');
formData.append('partnumber', 'ABC123');
formData.append('quantity', 100);
formData.append('datecode', '2024-Q1');
formData.append('category', 'Header');
formData.append('description', 'Details');
formData.append('price', '150');  // 單一價格
formData.append('product_img', imageFile);

fetch('/api/upload', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

#### 方式B：階梯價格（推薦）

```javascript
const priceTiers = [
  {"quantity": 1, "price": 150},
  {"quantity": 5, "price": 145},
  {"quantity": 10, "price": 140},
  {"quantity": 50, "price": 135},
  {"quantity": 100, "price": 130}
];

const formData = new FormData();
formData.append('brand', 'MOLEX');
formData.append('partnumber', 'ABC123');
formData.append('quantity', 100);
formData.append('datecode', '2024-Q1');
formData.append('category', 'Header');
formData.append('description', 'Details');
formData.append('price', JSON.stringify(priceTiers));  // 階梯價格
formData.append('product_img', imageFile);

fetch('/api/upload', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 2. 批量上傳 (Excel)

**URL:** `POST /api/batch-upload`

#### Excel 列結構 - 方式A：單一價格列

| partnumber | brand | dc       | qty | price | category | description |
|-----------|-------|----------|-----|-------|----------|-------------|
| ABC123    | MOLEX | 2024-Q1  | 100 | 150   | Header   | Details...  |
| XYZ789    | JST   | 2024-Q2  | 200 | 120   | Housing  | Details...  |

#### Excel 列結構 - 方式B：階梯價格列（推薦）

| partnumber | brand | dc       | qty | price_1 | price_5 | price_10 | price_50 | price_100 | category | description |
|-----------|-------|----------|-----|---------|---------|----------|----------|-----------|----------|-------------|
| ABC123    | MOLEX | 2024-Q1  | 100 | 150     | 145     | 140      | 135      | 130       | Header   | Details...  |
| XYZ789    | JST   | 2024-Q2  | 200 | 120     | 115     | 110      | 105      | 100       | Housing  | Details...  |

**系統會自動轉換為 JSON 格式存儲。**

### 3. 編輯產品

**URL:** `PUT /api/edit`

```javascript
const editData = {
  partnumber: 'ABC123',
  datecode: '2024-Q1',
  quantity: 150,
  price: [
    {"quantity": 1, "price": 155},
    {"quantity": 5, "price": 150},
    {"quantity": 10, "price": 145}
  ]
};

fetch('/api/edit', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(editData)
});
```

---

## 🔍 搜索與查詢

### 搜索端點

**URL:** `GET /api/search/<partnumber>?page=1&min_price=100&max_price=200`

**返回格式：**

```json
{
  "partnumber": "ABC123",
  "brand": "MOLEX",
  "dc": "2024-Q1",
  "qty": 100,
  "price": [
    {"quantity": 1, "price": 150},
    {"quantity": 5, "price": 145},
    {"quantity": 10, "price": 140}
  ],
  "category": "Header",
  "description": "Details..."
}
```

### 價格過濾邏輯

當用戶設置價格過濾範圍時（如 `min_price=130&max_price=150`），系統檢查：
- 產品的**最低價格**至少在範圍內

**前端展示示例：**

```javascript
// 取得搜索結果
const response = await fetch(`/api/search/ABC?page=1`);
const products = await response.json();

products.forEach(product => {
  if (Array.isArray(product.price)) {
    const prices = product.price.map(tier => 
      `${tier.quantity}pc: NT$${tier.price}`
    ).join(' | ');
    console.log(`${product.partnumber}: ${prices}`);
  }
});

// 輸出示例：
// ABC123: 1pc: NT$150 | 5pc: NT$145 | 10pc: NT$140
```

---

## 🔧 API 實現細節

### ProductManagementAPI

#### 上傳邏輯 (`upload_single_product`)

1. 接收 `price` 參數（可以是單一值或 JSON 陣列）
2. 調用 `_parse_tiered_price()` 解析
3. 轉換為 JSON 字符串存儲

#### 支持的價格格式

```python
# 格式1: 單一數值
price_input = "150"
# 結果: [{"quantity": 1, "price": 150}]

# 格式2: JSON 陣列字符串
price_input = '[{"quantity": 1, "price": 150}, {"quantity": 5, "price": 145}]'
# 結果: [{"quantity": 1, "price": 150}, {"quantity": 5, "price": 145}]

# 格式3: 浮點數
price_input = 150.50
# 結果: [{"quantity": 1, "price": 150.5}]
```

### UploadHistoryAPI

#### 批量上傳邏輯 (`_process_batch_upload`)

1. 讀取 Excel 文件
2. 檢測價格列：
   - 單一 `price` 列 → 包裝為階梯格式
   - 多個 `price_N` 列 → 直接解析為階梯格式
3. 驗證數據並轉換為 JSON
4. 使用 `INSERT ... ON DUPLICATE KEY UPDATE` 存儲

#### 支持的 Excel 列格式

```
✓ price           (單一價格)
✓ price_1         (1件單價)
✓ price_5         (5件單價)
✓ price_10        (10件單價)
✓ price_50        (50件單價)
✓ price_100       (100件單價)
```

系統會自動過濾空值，只保留有效的價格層級。

### ProductSearchAPI

#### 搜索邏輯 (`search_products`)

1. 執行 SQL 查詢
2. 對於每個結果，檢查 `price` 字段：
   - 如果已是 dict/list → 保持原樣
   - 如果是 JSON 字符串 → 解析為 JSON
   - 如果是純數值字符串 → 包裝為 `[{"quantity": 1, "price": X}]`
3. 返回 JSON 格式的結果

---

## 💡 使用場景示例

### 場景 1：展示產品價格信息

```html
<h3>ABC123 - MOLEX Header</h3>
<table>
  <tr>
    <th>數量 (PCS)</th>
    <th>單價 (NT$)</th>
  </tr>
  <!-- 前端 JavaScript 生成 -->
  <tr>
    <td>1 - 4</td>
    <td>150</td>
  </tr>
  <tr>
    <td>5 - 9</td>
    <td>145</td>
  </tr>
  <tr>
    <td>10+</td>
    <td>140</td>
  </tr>
</table>
```

### 場景 2：計算客戶購買成本

```javascript
function calculateOrderCost(product, quantity) {
  if (!Array.isArray(product.price)) {
    return quantity * product.price[0].price;
  }
  
  // 找到適用的價格層級
  let applicablePrice = product.price[0].price;
  for (let tier of product.price) {
    if (quantity >= tier.quantity) {
      applicablePrice = tier.price;
    }
  }
  
  return quantity * applicablePrice;
}

// 示例
const product = {
  partnumber: 'ABC123',
  price: [
    {"quantity": 1, "price": 150},
    {"quantity": 5, "price": 145},
    {"quantity": 10, "price": 140}
  ]
};

console.log(calculateOrderCost(product, 1));   // 150
console.log(calculateOrderCost(product, 5));   // 725 (145*5)
console.log(calculateOrderCost(product, 10));  // 1400 (140*10)
console.log(calculateOrderCost(product, 20));  // 2800 (140*20)
```

---

## ⚙️ 配置與擴展

### 添加自定義價格層級

如需支持其他數量層級（如 200, 500 等），在 Excel 中添加對應列：

```
price_200, price_500, price_1000
```

系統會自動檢測並處理。

### 數據庫查詢示例

```sql
-- 獲取產品的所有價格層級
SELECT id, partnumber, price FROM products WHERE partnumber = 'ABC123';

-- 結果：price 列包含 JSON 數據
[{"quantity": 1, "price": 150}, {"quantity": 5, "price": 145}]

-- 提取特定層級的價格
SELECT JSON_EXTRACT(price, '$[1].price') FROM products WHERE partnumber = 'ABC123';
-- 結果: 145
```

---

## 🐛 故障排除

### 常見問題

**Q: 上傳時出現「Invalid price format」錯誤**

A: 確保價格格式正確：
- 單一價格：`"150"` 或 `150`
- JSON 陣列：`'[{"quantity": 1, "price": 150}]'`

**Q: Excel 批量上傳沒有保存價格**

A: 檢查 Excel 列名
- ✓ 正確：`price`, `price_1`, `price_5`
- ✗ 錯誤：`Price`（大寫), `price 1`（有空格）

**Q: 搜索結果中價格顯示異常**

A: 確認數據庫遷移已執行：
```python
from api.utils.migrations import convert_price_to_json
convert_price_to_json()
```

---

## 📊 性能考慮

- **JSON 存儲效率高**，單個產品的陣列通常 &lt; 500 bytes
- **建議為 `(partnumber, upload_user, dc)` 創建複合索引**以加速查詢
- **價格層級數量無限制**，建議保持在 5-10 層以平衡功能與性能

---

## 🚀 後續擴展

### 建議的增強功能

1. **批量價格更新** - 允許快速編輯多個產品的價格層級
2. **價格歷史追蹤** - 記錄價格變更歷史
3. **動態價格計算** - 基於成本和利潤自動生成層級
4. **客戶專屬價格** - 不同客戶享受不同的價格層級

---

**文件更新日期**: 2026.03.10
**版本**: 1.0
