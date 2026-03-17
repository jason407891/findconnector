// API 配置
const API_BASE_URL = '/api';
const TOKEN_KEYS = ['auth_token', 'token'];

function getToken() {
    const token = localStorage.getItem(TOKEN_KEYS[0]) || localStorage.getItem(TOKEN_KEYS[1]);
    return token === 'null' || !token ? null : token;
}

let currentEditingUserId = null;
let currentEditingProductId = null;
let currentUserPage = 1;
let currentProductPage = 1;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    const token = getToken();
    if (!token) {
        alert('請先登入');
        window.location.href = '/';
        return;
    }

    // 加載儀表板數據
    loadStatistics();

    // 搜尋監聽器
    document.getElementById('userSearch').addEventListener('keyup', function() {
        currentUserPage = 1;
        loadUsers();
    });

    document.getElementById('productSearch').addEventListener('keyup', function() {
        currentProductPage = 1;
        loadProducts();
    });

    document.getElementById('productStatus').addEventListener('change', function() {
        currentProductPage = 1;
        loadProducts();
    });
});

// ===== 面板切換 =====

function switchPanel(panelName) {
    // 隱藏所有面板
    document.querySelectorAll('.content-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // 移除所有菜單的 active 類
    document.querySelectorAll('.menu-link').forEach(link => {
        link.classList.remove('active');
    });

    // 顯示選定的面板
    document.getElementById(panelName).classList.add('active');
    event.currentTarget.classList.add('active');

    // 加載相應的數據
    if (panelName === 'users') {
        loadUsers();
    } else if (panelName === 'products') {
        loadProducts();
    }
}

// ===== 儀表板 =====

function loadStatistics() {
    const token = getToken();
    const statisticsDiv = document.getElementById('statistics');

    fetch(`${API_BASE_URL}/admin/statistics`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            statisticsDiv.innerHTML = `<div class="loading" style="color: #999;">加載失敗</div>`;
            return;
        }

        statisticsDiv.innerHTML = `
            <div class="stat-card users">
                <div class="stat-label">總用戶數</div>
                <div class="stat-value">${data.total_users}</div>
            </div>
            <div class="stat-card products">
                <div class="stat-label">總產品數</div>
                <div class="stat-value">${data.total_products}</div>
            </div>
            <div class="stat-card pending">
                <div class="stat-label">待審核產品</div>
                <div class="stat-value">${data.pending_products}</div>
            </div>
            <div class="stat-card chats">
                <div class="stat-label">活躍聊天</div>
                <div class="stat-value">${data.active_chats}</div>
            </div>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
        statisticsDiv.innerHTML = `<div class="loading" style="color: #999;">加載出錯</div>`;
    });
}

// ===== 用戶管理 =====

function loadUsers() {
    const token = getToken();
    const search = document.getElementById('userSearch').value;
    const usersTableDiv = document.getElementById('usersTable');

    const url = new URL(`${window.location.origin}${API_BASE_URL}/admin/users`);
    url.searchParams.set('page', currentUserPage);
    if (search) url.searchParams.set('search', search);

    fetch(url.toString(), {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            usersTableDiv.innerHTML = `<div class="loading" style="color: #999;">加載失敗</div>`;
            return;
        }

        renderUsersTable(data);
    })
    .catch(error => {
        console.error('Error:', error);
        usersTableDiv.innerHTML = `<div class="loading" style="color: #999;">加載出錯</div>`;
    });
}

function renderUsersTable(data) {
    const usersTableDiv = document.getElementById('usersTable');

    if (data.users.length === 0) {
        usersTableDiv.innerHTML = `<div style="padding: 20px; text-align: center; color: #999;">暫無用戶</div>`;
        return;
    }

    const tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>用戶名</th>
                    <th>郵箱</th>
                    <th>公司</th>
                    <th>角色</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${data.users.map(user => `
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.user_name}</td>
                        <td>${user.user_email}</td>
                        <td>${user.company_name || '-'}</td>
                        <td><span class="badge badge-pending">${user.role}</span></td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-small btn-edit" onclick="editUser(${user.id})">編輯</button>
                                <button class="btn-small btn-delete" onclick="deleteUser(${user.id})">刪除</button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <div class="pagination">
            ${data.page > 1 ? `<button onclick="previousUserPage()">← 上一頁</button>` : ''}
            <span style="padding: 8px 12px;">第 ${data.page} / ${data.pages} 頁</span>
            ${data.page < data.pages ? `<button onclick="nextUserPage()">下一頁 →</button>` : ''}
        </div>
    `;

    usersTableDiv.innerHTML = tableHTML;
}

function editUser(userId) {
    const token = localStorage.getItem(TOKEN_KEY);

    fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(user => {
        if (user.error) {
            alert('加載用戶信息失敗');
            return;
        }

        currentEditingUserId = userId;
        document.getElementById('userName').value = user.user_name;
        document.getElementById('userEmail').value = user.user_email;
        document.getElementById('userCompany').value = user.company_name || '';
        document.getElementById('userPhone').value = user.phone_number || '';
        document.getElementById('userAddress').value = user.warehouse_address || '';
        document.getElementById('userRole').value = user.role;

        document.getElementById('editUserModal').classList.add('show');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('加載用戶信息失敗');
    });
}

function closeEditUserModal() {
    document.getElementById('editUserModal').classList.remove('show');
    hideUserModalAlert();
}

function saveUserChanges() {
    const token = localStorage.getItem(TOKEN_KEY);
    const saveBtn = event.currentTarget;
    saveBtn.disabled = true;

    const userData = {
        user_name: document.getElementById('userName').value,
        company_name: document.getElementById('userCompany').value,
        phone_number: document.getElementById('userPhone').value,
        warehouse_address: document.getElementById('userAddress').value,
        role: document.getElementById('userRole').value
    };

    fetch(`${API_BASE_URL}/admin/users/${currentEditingUserId}`, {
        method: 'PUT',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showUserModalAlert('保存失敗：' + data.message, 'error');
            return;
        }

        closeEditUserModal();
        loadUsers();
        alert('用戶信息已保存');
    })
    .catch(error => {
        console.error('Error:', error);
        showUserModalAlert('保存失敗', 'error');
    })
    .finally(() => {
        saveBtn.disabled = false;
    });
}

function deleteUser(userId) {
    if (!confirm('確定要刪除此用戶嗎？')) return;

    const token = localStorage.getItem(TOKEN_KEY);

    fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('刪除失敗：' + data.message);
            return;
        }

        alert('用戶已刪除');
        loadUsers();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('刪除失敗');
    });
}

function nextUserPage() {
    currentUserPage++;
    loadUsers();
    document.querySelector('#usersTable').scrollIntoView();
}

function previousUserPage() {
    currentUserPage--;
    loadUsers();
    document.querySelector('#usersTable').scrollIntoView();
}

// ===== 產品管理 =====

function loadProducts() {
    const token = localStorage.getItem(TOKEN_KEY);
    const search = document.getElementById('productSearch').value;
    const status = document.getElementById('productStatus').value;
    const productsTableDiv = document.getElementById('productsTable');

    const url = new URL(`${window.location.origin}${API_BASE_URL}/admin/products`);
    url.searchParams.set('page', currentProductPage);
    if (search) url.searchParams.set('search', search);
    if (status) url.searchParams.set('status', status);

    fetch(url.toString(), {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            productsTableDiv.innerHTML = `<div class="loading" style="color: #999;">加載失敗</div>`;
            return;
        }

        renderProductsTable(data);
    })
    .catch(error => {
        console.error('Error:', error);
        productsTableDiv.innerHTML = `<div class="loading" style="color: #999;">加載出錯</div>`;
    });
}

function renderProductsTable(data) {
    const productsTableDiv = document.getElementById('productsTable');

    if (data.products.length === 0) {
        productsTableDiv.innerHTML = `<div style="padding: 20px; text-align: center; color: #999;">暫無產品</div>`;
        return;
    }

    const tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>部件號</th>
                    <th>品牌</th>
                    <th>數量</th>
                    <th>價格</th>
                    <th>狀態</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${data.products.map(product => `
                    <tr>
                        <td>${product.id}</td>
                        <td>${product.partnumber}</td>
                        <td>${product.brand}</td>
                        <td>${product.qty}</td>
                        <td>$${parseFloat(product.price).toFixed(2)}</td>
                        <td><span class="badge badge-${product.status}">${getStatusLabel(product.status)}</span></td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-small btn-edit" onclick="editProduct(${product.id})">編輯</button>
                                ${product.status === 'pending' ? `
                                    <button class="btn-small btn-approve" onclick="approveProduct(${product.id})">批准</button>
                                    <button class="btn-small btn-reject" onclick="rejectProduct(${product.id})">拒絕</button>
                                ` : ''}
                                <button class="btn-small btn-delete" onclick="deleteProduct(${product.id})">刪除</button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <div class="pagination">
            ${data.page > 1 ? `<button onclick="previousProductPage()">← 上一頁</button>` : ''}
            <span style="padding: 8px 12px;">第 ${data.page} / ${data.pages} 頁</span>
            ${data.page < data.pages ? `<button onclick="nextProductPage()">下一頁 →</button>` : ''}
        </div>
    `;

    productsTableDiv.innerHTML = tableHTML;
}

function editProduct(productId) {
    const token = localStorage.getItem(TOKEN_KEY);

    fetch(`${API_BASE_URL}/admin/products/${productId}`, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(product => {
        if (product.error) {
            alert('加載產品信息失敗');
            return;
        }

        currentEditingProductId = productId;
        document.getElementById('productPartNumber').value = product.partnumber;
        document.getElementById('productBrand').value = product.brand || '';
        document.getElementById('productQty').value = product.qty || 0;
        document.getElementById('productPrice').value = product.price || 0;
        document.getElementById('productCategory').value = product.category || '';
        document.getElementById('productDescription').value = product.description || '';

        document.getElementById('editProductModal').classList.add('show');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('加載產品信息失敗');
    });
}

function closeEditProductModal() {
    document.getElementById('editProductModal').classList.remove('show');
    hideProductModalAlert();
}

function saveProductChanges() {
    const token = localStorage.getItem(TOKEN_KEY);
    const saveBtn = event.currentTarget;
    saveBtn.disabled = true;

    const productData = {
        brand: document.getElementById('productBrand').value,
        qty: parseInt(document.getElementById('productQty').value),
        price: parseFloat(document.getElementById('productPrice').value),
        category: document.getElementById('productCategory').value,
        description: document.getElementById('productDescription').value
    };

    fetch(`${API_BASE_URL}/admin/products/${currentEditingProductId}`, {
        method: 'PUT',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(productData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showProductModalAlert('保存失敗：' + data.message, 'error');
            return;
        }

        closeEditProductModal();
        loadProducts();
        alert('產品信息已保存');
    })
    .catch(error => {
        console.error('Error:', error);
        showProductModalAlert('保存失敗', 'error');
    })
    .finally(() => {
        saveBtn.disabled = false;
    });
}

function approveProduct(productId) {
    if (!confirm('確定要批准此產品嗎？')) return;

    const token = localStorage.getItem(TOKEN_KEY);

    fetch(`${API_BASE_URL}/admin/products/${productId}/approve`, {
        method: 'PUT',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('操作失敗：' + data.message);
            return;
        }

        alert('產品已批准');
        loadProducts();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失敗');
    });
}

function rejectProduct(productId) {
    const reason = prompt('請輸入拒絕原因：');
    if (reason === null) return;

    const token = localStorage.getItem(TOKEN_KEY);

    fetch(`${API_BASE_URL}/admin/products/${productId}/reject`, {
        method: 'PUT',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: reason })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('操作失敗：' + data.message);
            return;
        }

        alert('產品已拒絕');
        loadProducts();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('操作失敗');
    });
}

function deleteProduct(productId) {
    if (!confirm('確定要刪除此產品嗎？')) return;

    const token = localStorage.getItem(TOKEN_KEY);

    fetch(`${API_BASE_URL}/admin/products/${productId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('刪除失敗：' + data.message);
            return;
        }

        alert('產品已刪除');
        loadProducts();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('刪除失敗');
    });
}

function nextProductPage() {
    currentProductPage++;
    loadProducts();
    document.querySelector('#productsTable').scrollIntoView();
}

function previousProductPage() {
    currentProductPage--;
    loadProducts();
    document.querySelector('#productsTable').scrollIntoView();
}

// ===== 工具函數 =====

function getStatusLabel(status) {
    const labels = {
        'published': '已發布',
        'pending': '待審核',
        'rejected': '已拒絕',
        'open': '開放',
        'closed': '已關閉'
    };
    return labels[status] || status;
}

function showUserModalAlert(message, type) {
    const alert = document.getElementById('userModalAlert');
    alert.textContent = message;
    alert.className = `alert show alert-${type}`;
}

function hideUserModalAlert() {
    const alert = document.getElementById('userModalAlert');
    alert.className = 'alert';
}

function showProductModalAlert(message, type) {
    const alert = document.getElementById('productModalAlert');
    alert.textContent = message;
    alert.className = `alert show alert-${type}`;
}

function hideProductModalAlert() {
    const alert = document.getElementById('productModalAlert');
    alert.className = 'alert';
}

function logout() {
    if (confirm('確定要登出嗎？')) {
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = '/';
    }
}

// 關閉模態框（點擊外部）
document.addEventListener('click', function(event) {
    const userModal = document.getElementById('editUserModal');
    const productModal = document.getElementById('editProductModal');

    if (event.target === userModal) {
        closeEditUserModal();
    }
    if (event.target === productModal) {
        closeEditProductModal();
    }
});
