/**
 * Brand listing page functionality
 * Fetches unique brands from database and displays them grouped by alphabetical order
 */

// Store brands data
let allBrands = [];
let groupedBrands = {};

/**
 * Load brands from API
 */
async function loadBrands() {
    try {
        const response = await fetch('/api/manufacturer');
        if (!response.ok) {
            throw new Error('Failed to fetch brands');
        }
        
        const data = await response.json();
        
        // Extract brand names from response
        allBrands = data.map(item => item.brand).filter(brand => brand && brand.trim());
        
        // Remove duplicates (just in case)
        allBrands = [...new Set(allBrands)];
        
        // Sort alphabetically
        allBrands.sort((a, b) => a.localeCompare(b, 'en', { sensitivity: 'base' }));
        
        // Group by first letter
        groupBrandsByLetter();
        
        // Display brands
        renderBrands();
        
        // Render navigation
        renderNavigation();
        
    } catch (error) {
        console.error('Error loading brands:', error);
        document.querySelector('.brandlist').textContent = '品牌加載失敗，請稍後重試';
    }
}

/**
 * Group brands by their first letter (uppercase)
 */
function groupBrandsByLetter() {
    groupedBrands = {};
    
    allBrands.forEach(brand => {
        const firstLetter = brand.charAt(0).toUpperCase();
        if (!groupedBrands[firstLetter]) {
            groupedBrands[firstLetter] = [];
        }
        groupedBrands[firstLetter].push(brand);
    });
}

/**
 * Render the alphabet navigation bar
 */
function renderNavigation() {
    const letters = Object.keys(groupedBrands).sort();
    const navBar = document.querySelector('.brandjump');
    navBar.innerHTML = '';
    
    letters.forEach(letter => {
        const span = document.createElement('span');
        span.textContent = letter;
        span.style.cursor = 'pointer';
        span.style.marginRight = '5px';
        span.style.padding = '5px 10px';
        span.style.borderRadius = '3px';
        span.style.transition = 'background-color 0.2s';
        
        span.addEventListener('mouseover', () => {
            span.style.backgroundColor = '#f0f0f0';
        });
        
        span.addEventListener('mouseout', () => {
            span.style.backgroundColor = 'transparent';
        });
        
        span.addEventListener('click', () => {
            scrollToLetter(letter);
        });
        
        navBar.appendChild(span);
    });
}

/**
 * Render all brands grouped by letter
 */
function renderBrands() {
    const container = document.querySelector('body');
    
    // Remove existing brand items (keep header and navigation)
    const existingAlphabets = document.querySelectorAll('.alphabet');
    const existingAreas = document.querySelectorAll('.brandarea');
    
    existingAlphabets.forEach(el => el.remove());
    existingAreas.forEach(el => el.remove());
    
    // Get sorted letters
    const letters = Object.keys(groupedBrands).sort();
    
    // Find the position to insert after brandjump
    const brandjump = document.querySelector('.brandjump');
    let insertAfter = brandjump;
    
    // Render each letter group
    letters.forEach(letter => {
        // Create alphabet header
        const alphabetDiv = document.createElement('div');
        alphabetDiv.className = 'alphabet';
        alphabetDiv.id = `letter-${letter}`;
        alphabetDiv.textContent = letter;
        insertAfter.parentNode.insertBefore(alphabetDiv, insertAfter.nextSibling);
        insertAfter = alphabetDiv;
        
        // Create brand area
        const brandareaDiv = document.createElement('div');
        brandareaDiv.className = 'brandarea';
        
        // Add brands
        groupedBrands[letter].forEach(brand => {
            const brandDiv = document.createElement('div');
            brandDiv.textContent = brand;
            brandDiv.style.cursor = 'pointer';
            brandDiv.style.transition = 'all 0.2s';
            
            // Add hover effect
            brandDiv.addEventListener('mouseover', () => {
                brandDiv.style.backgroundColor = '#e8e8e8';
                brandDiv.style.transform = 'scale(1.05)';
            });
            
            brandDiv.addEventListener('mouseout', () => {
                brandDiv.style.backgroundColor = 'transparent';
                brandDiv.style.transform = 'scale(1)';
            });
            
            // Navigate to product search with brand filter
            brandDiv.addEventListener('click', () => {
                searchByBrand(brand);
            });
            
            brandareaDiv.appendChild(brandDiv);
        });
        
        insertAfter.parentNode.insertBefore(brandareaDiv, insertAfter.nextSibling);
        insertAfter = brandareaDiv;
    });
    
    // Update title with total count
    const brandlist = document.querySelector('.brandlist');
    brandlist.textContent = `所有品牌列表 (共 ${allBrands.length} 個品牌)`;
}

/**
 * Scroll to a specific letter section
 */
function scrollToLetter(letter) {
    const element = document.getElementById(`letter-${letter}`);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Search products by brand
 */
function searchByBrand(brand) {
    // Redirect to product search page with brand filter
    // Assuming there's a search or product page
    window.location.href = `/product?brand=${encodeURIComponent(brand)}`;
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    loadBrands();
});
