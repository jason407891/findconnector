/**
 * Category listing page functionality
 * Fetches all unique categories from database and displays them
 */

// Store categories data
let allCategories = [];

/**
 * Load categories from API
 */
async function loadCategories() {
    try {
        const response = await fetch('/api/showcategories');
        if (!response.ok) {
            throw new Error('Failed to fetch categories');
        }
        
        const data = await response.json();
        
        // Extract category names from response
        // Handle both array and object responses
        if (Array.isArray(data)) {
            allCategories = data
                .map(item => typeof item === 'string' ? item : item.category)
                .filter(cat => cat && cat.trim());
        } else {
            allCategories = Object.values(data)
                .filter(cat => cat && cat.trim());
        }
        
        // Remove duplicates
        allCategories = [...new Set(allCategories)];
        
        // Sort alphabetically
        allCategories.sort((a, b) => a.localeCompare(b, 'en', { sensitivity: 'base' }));
        
        // Display categories
        renderCategories();
        
    } catch (error) {
        console.error('Error loading categories:', error);
        document.querySelector('.category_title').textContent = '分類加載失敗，請稍後重試';
    }
}

/**
 * Render all categories in a grid layout
 */
function renderCategories() {
    const container = document.querySelector('.categories_grid');
    container.innerHTML = '';
    
    const title = document.querySelector('.category_title');
    title.textContent = `產品分類 (共 ${allCategories.length} 個分類)`;
    
    // Create category cards
    allCategories.forEach((category, index) => {
        const categoryCard = document.createElement('div');
        categoryCard.className = 'category_card';
        categoryCard.style.cursor = 'pointer';
        categoryCard.style.transition = 'all 0.3s ease';
        categoryCard.innerHTML = `
            <div class="category_card_icon">📦</div>
            <div class="category_card_name">${escapeHtml(category)}</div>
        `;
        
        // Add hover effect
        categoryCard.addEventListener('mouseover', () => {
            categoryCard.style.transform = 'translateY(-5px)';
            categoryCard.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.2)';
            categoryCard.style.backgroundColor = '#f9f9f9';
        });
        
        categoryCard.addEventListener('mouseout', () => {
            categoryCard.style.transform = 'translateY(0)';
            categoryCard.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
            categoryCard.style.backgroundColor = 'white';
        });
        
        // Navigate to category products
        categoryCard.addEventListener('click', () => {
            searchByCategory(category);
        });
        
        container.appendChild(categoryCard);
    });
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Search products by category
 */
function searchByCategory(category) {
    // Redirect to product search page with category filter
    window.location.href = `/product?category=${encodeURIComponent(category)}`;
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
});
