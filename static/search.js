// Enhanced Search Page JavaScript
// AI Product Finder - Modern Search Implementation
// Author: Aditya Tripathi

let currentPage = 1;
let totalPages = 1;
let currentQuery = '';
let currentFilters = {};
let priceValidationTimeout;
let searchTimeout;

// Show loading state
function showLoadingState() {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = `
        <div class="search-loading">
            <div class="loading-spinner"></div>
            <div class="search-loading-text">Searching through our product database...</div>
        </div>
    `;
}

// Hide loading state and show results
function hideLoadingState() {
    const loadingState = document.getElementById('loadingState');
    if (loadingState) {
        loadingState.style.display = 'none';
    }
}

// Enhanced search with debouncing
function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        performSearch();
    }, 500);
}

// Modal functionality
const modal = document.getElementById('productModal');
const modalClose = document.getElementsByClassName('modal-close')[0];

if (modalClose) {
    modalClose.onclick = function() {
        modal.style.display = 'none';
    }
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Show product details in popup
function showProductDetails(product) {
  const modalBody = document.getElementById('modalBody');
  
  // Get all product fields
  const fields = Object.keys(product);
  const detailsHTML = fields.map(key => {
    if (key === 'price' || key.toLowerCase().includes('price')) {
      return `
        <div class="detail-item">
          <div class="detail-label">${key}</div>
          <div class="detail-value product-price">₹${product[key]}</div>
        </div>
      `;
    }
    return `
      <div class="detail-item">
        <div class="detail-label">${key}</div>
        <div class="detail-value">${product[key] || 'N/A'}</div>
      </div>
    `;
  }).join('');
  
  modalBody.innerHTML = `
    <div class="product-header">
      <div>
        <h2 class="product-title">${product.brand || product.Brand || ''} ${product.model || product.Model || product.name || product.Name || 'Product'}</h2>
      </div>
    </div>
    <div class="product-details">
      ${detailsHTML}
    </div>
  `;
  
  modal.style.display = 'block';
}

// Create product card
function createProductCard(product) {
  const card = document.createElement('div');
  card.className = 'product-card-modern';
  
  // Standardize field names and handle various data formats across different datasets
  const brand = product.Brand || product.brand || product.Company || product.company || '';
  
  // Handle different naming conventions for model/name across datasets
  let model = '';
  if (product.Name) {
    // For laptop data, extract clean model name from the complex Name field
    model = product.Name.split('::')[0] || product.Name;
    // Remove brand name from the beginning if it exists
    if (brand && model.toLowerCase().startsWith(brand.toLowerCase())) {
      model = model.substring(brand.length).trim();
    }
  } else {
    model = product.Model || product.model || product.Title || product.name || product.Product || '';
  }
  
  // If we still don't have a model name, construct one
  if (!model || model.trim() === '') {
    model = `${brand} Product` || 'Product';
  }
  
  // Find price from various possible column names specific to each dataset
  let price = product.Price || product['Selling Price'] || product.Selling_Price || 
              product.price || product.selling_price || product.Actual_Price || 
              product.actual_price;
  
  // Format price with proper number formatting
  if (price && price !== 'N/A' && price !== '' && price !== null && price !== undefined) {
    // Remove any non-numeric characters except decimal points and commas
    const cleanPrice = String(price).replace(/[^\d.,]/g, '');
    if (cleanPrice && cleanPrice !== '') {
      try {
        // Handle both comma and dot as decimal separators
        const numericPrice = parseFloat(cleanPrice.replace(/,/g, ''));
        if (!isNaN(numericPrice) && numericPrice > 0) {
          price = numericPrice.toLocaleString('en-IN');
        } else {
          price = 'Price on request';
        }
      } catch (e) {
        price = 'Price on request';
      }
    } else {
      price = 'Price on request';
    }
  } else {
    price = 'Price on request';
  }
  
  // Get key specifications with better organization
  const excludeFields = [
    'brand', 'Brand', 'model', 'Model', 'name', 'Name', 'Title', 'Product',
    'price', 'Price', 'selling_price', 'Selling_Price', 'Company', 'company',
    'Actual_Price', 'actual_price', 'selling price', 'Selling Price', 'Original Price',
    'Color', 'Colour', 'colour', 'color' // Exclude color as it's usually not critical
  ];
  
  const allSpecs = Object.keys(product).filter(key => 
    !excludeFields.includes(key) && 
    product[key] !== '' && 
    product[key] !== null && 
    product[key] !== undefined &&
    product[key] !== 'No' &&
    product[key] !== 'N/A' &&
    String(product[key]).trim() !== ''
  );
  
  // Prioritize important specs based on product type
  const prioritySpecs = [
    // Laptop specs
    'RAM', 'ram', 'Memory', 'Storage', 'storage', 'Processor_Name', 'processor', 'Display', 'display',
    'GPU', 'Graphics', 'SSD', 'HDD', 'Battery_Life', 'Processor_Brand',
    // Mobile specs  
    'Memory', 'Storage', 'Rating', 'rating',
    // Headphone specs
    'Form_Factor', 'Connectivity_Type', 'Playtime'
  ];
  
  const importantSpecs = allSpecs.filter(key => 
    prioritySpecs.some(priority => key.toLowerCase().includes(priority.toLowerCase()))
  ).slice(0, 3);
  
  const otherSpecs = allSpecs.filter(key => 
    !importantSpecs.includes(key)
  ).slice(0, 4 - importantSpecs.length);
  
  const specs = [...importantSpecs, ...otherSpecs];
  
  const specsHTML = specs.map(key => {
    let value = product[key];
    // Truncate long values for better display
    if (typeof value === 'string' && value.length > 30) {
      value = value.substring(0, 27) + '...';
    }
    
    return `
      <div class="detail-item-modern">
        <div class="detail-label-modern">${formatFieldName(key)}</div>
        <div class="detail-value-modern">${value || 'N/A'}</div>
      </div>
    `;
  }).join('');
  
  // Create rating/score if available
  let ratingHTML = '';
  const rating = product.Rating || product.rating;
  if (rating && rating !== 'N/A' && rating !== '') {
    const ratingNum = parseFloat(rating);
    if (!isNaN(ratingNum)) {
      const stars = '★'.repeat(Math.floor(ratingNum)) + '☆'.repeat(5 - Math.floor(ratingNum));
      ratingHTML = `
        <div class="product-rating">
          <span class="rating-stars">${stars}</span>
          <span class="rating-value">${rating}</span>
        </div>
      `;
    }
  }
  
  card.innerHTML = `
    <div class="product-card-header">
      <div class="product-info">
        <div class="product-title-modern">${model}</div>
        ${brand ? `<div class="product-brand-modern">${brand}</div>` : ''}
        ${ratingHTML}
      </div>
      <div class="product-price-modern">
        <span class="currency">₹</span>
        <span class="price-value">${price}</span>
      </div>
    </div>
    <div class="product-details-modern">
      ${specsHTML}
    </div>
    <div class="product-actions">
      <button class="view-details-btn-modern">
        <span class="btn-icon">👁️</span>
        <span class="btn-text">View Details</span>
      </button>
    </div>
  `;
  
  card.querySelector('.view-details-btn-modern').addEventListener('click', () => {
    showProductDetails(product);
  });
  
  return card;
}

// Helper function to format field names for display
function formatFieldName(fieldName) {
  // Convert camelCase and snake_case to readable format
  return fieldName
    .replace(/([A-Z])/g, ' $1') // Add space before capital letters
    .replace(/_/g, ' ') // Replace underscores with spaces
    .replace(/\b\w/g, l => l.toUpperCase()) // Capitalize first letter of each word
    .trim();
}

// Display search results
function displayResults(data) {
  const container = document.getElementById('resultsContainer');
  
  if (!data.results || data.results.length === 0) {
    container.innerHTML = `
      <div class="empty-state-modern">
        <div class="empty-icon-modern">🔍</div>
        <h3 class="empty-title">No Results Found</h3>
        <p class="empty-description">Try adjusting your search criteria or filters</p>
        <div class="search-suggestions">
          <p class="suggestions-title">Suggestions:</p>
          <div class="suggestion-tags">
            <span class="suggestion-tag" onclick="document.getElementById('searchQuery').value=''; document.getElementById('category').selectedIndex=0; document.getElementById('searchBtn').click();">Clear all filters</span>
            <span class="suggestion-tag" onclick="document.getElementById('searchQuery').value='laptop'; document.getElementById('searchBtn').click();">Search laptops</span>
            <span class="suggestion-tag" onclick="document.getElementById('searchQuery').value='mobile'; document.getElementById('searchBtn').click();">Search mobiles</span>
          </div>
        </div>
      </div>
    `;
    document.getElementById('pagination').innerHTML = '';
    return;
  }
  
  // Create results header with count and sorting info
  const resultsHeader = document.createElement('div');
  resultsHeader.className = 'results-header-modern';
  resultsHeader.innerHTML = `
    <div class="results-info">
      <h3 class="results-count">
        <span class="results-number">${data.total || data.results.length}</span> 
        <span class="results-text">products found</span>
      </h3>
      ${data.page ? `<span class="page-info">Page ${data.page} of ${data.total_pages || 1}</span>` : ''}
    </div>
    <div class="results-actions">
      <div class="view-toggle">
        <button class="view-btn active" data-view="grid" title="Grid View">
          <span class="view-icon">⊞</span>
        </button>
        <button class="view-btn" data-view="list" title="List View">
          <span class="view-icon">☰</span>
        </button>
      </div>
    </div>
  `;
  
  // Create results grid
  const grid = document.createElement('div');
  grid.className = 'results-grid-modern';
  grid.id = 'resultsGrid';
  
  data.results.forEach(product => {
    grid.appendChild(createProductCard(product));
  });
  
  // Clear container and add new content
  container.innerHTML = '';
  container.appendChild(resultsHeader);
  container.appendChild(grid);
  
  // Add view toggle functionality
  const viewButtons = container.querySelectorAll('.view-btn');
  viewButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      viewButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const view = btn.dataset.view;
      const resultsGrid = document.getElementById('resultsGrid');
      
      if (view === 'list') {
        resultsGrid.className = 'results-list-modern';
      } else {
        resultsGrid.className = 'results-grid-modern';
      }
    });
  });
  
  // Update pagination
  totalPages = data.total_pages || 1;
  currentPage = data.page || 1;
  renderPagination();
}

// Render pagination
function renderPagination() {
  const paginationContainer = document.getElementById('pagination');
  
  if (totalPages <= 1) {
    paginationContainer.innerHTML = '';
    return;
  }
  
  let html = '';
  
  // Previous button
  html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">← Prev</button>`;
  
  // Page numbers
  for (let i = 1; i <= Math.min(totalPages, 10); i++) {
    html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }
  
  if (totalPages > 10) {
    html += `<button disabled>...</button>`;
    html += `<button onclick="goToPage(${totalPages})">${totalPages}</button>`;
  }
  
  // Next button
  html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next →</button>`;
  
  paginationContainer.innerHTML = html;
}

// Go to specific page
function goToPage(page) {
  if (page < 1 || page > totalPages || page === currentPage) return;
  currentPage = page;
  performSearch();
}

// Validate price range
function validatePriceRange(minPrice, maxPrice) {
  const min = parseFloat(minPrice);
  const max = parseFloat(maxPrice);
  
  if (minPrice && maxPrice && min >= max) {
    return {
      valid: false,
      message: 'Minimum price must be less than maximum price'
    };
  }
  
  if (min < 0 || max < 0) {
    return {
      valid: false, 
      message: 'Price values must be positive'
    };
  }
  
  return { valid: true };
}

// Show error message
function showErrorMessage(message) {
  const resultsContainer = document.getElementById('resultsContainer');
  resultsContainer.innerHTML = `
    <div class="error-state-modern">
      <div class="error-icon-modern">⚠️</div>
      <h3 class="error-title">Invalid Input</h3>
      <p class="error-description">${message}</p>
    </div>
  `;
}

// Perform search
async function performSearch() {
  const query = document.getElementById('searchQuery').value.trim();
  const category = document.getElementById('category').value;
  const minPrice = document.getElementById('minPrice').value;
  const maxPrice = document.getElementById('maxPrice').value;
  const fields = document.getElementById('fields').value;
  const perPage = document.getElementById('perPage').value;
  
  if (!query) {
    showErrorMessage('Please enter a search query');
    return;
  }
  
  // Validate price range
  const priceValidation = validatePriceRange(minPrice, maxPrice);
  if (!priceValidation.valid) {
    showErrorMessage(priceValidation.message);
    return;
  }
  
  currentQuery = query;
  currentFilters = { category, minPrice, maxPrice, fields, perPage };
  
  // Show loading
  document.getElementById('resultsContainer').innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p>Searching...</p>
    </div>
  `;
  
  try {
    // Build query parameters
    const params = new URLSearchParams({
      q: query,
      page: currentPage,
      per_page: perPage || 10
    });
    
    if (category) params.append('category', category);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    if (fields) params.append('fields', fields);
    
    const response = await fetch(`/search?${params.toString()}`);
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    displayResults(data);
  } catch (error) {
    document.getElementById('resultsContainer').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">❌</div>
        <h3>Error</h3>
        <p>${error.message}</p>
      </div>
    `;
  }
}

// Real-time price range validation
function validatePriceRangeRealtime() {
  const minPriceInput = document.getElementById('minPrice');
  const maxPriceInput = document.getElementById('maxPrice');
  const priceRangeContainer = minPriceInput.closest('.price-range');
  
  clearTimeout(priceValidationTimeout);
  priceValidationTimeout = setTimeout(() => {
    const minPrice = minPriceInput.value;
    const maxPrice = maxPriceInput.value;
    const validation = validatePriceRange(minPrice, maxPrice);
    
    // Remove existing error states
    priceRangeContainer.classList.remove('price-range-error');
    const existingError = priceRangeContainer.querySelector('.price-error-message');
    if (existingError) existingError.remove();
    
    if (!validation.valid && (minPrice || maxPrice)) {
      // Add error styling
      priceRangeContainer.classList.add('price-range-error');
      
      // Add error message
      const errorDiv = document.createElement('div');
      errorDiv.className = 'price-error-message';
      errorDiv.textContent = validation.message;
      priceRangeContainer.insertAdjacentElement('afterend', errorDiv);
    }
  }, 300);
}

// Clear all filters function
function clearFilters() {
  // Clear text inputs
  const inputs = ['searchQuery', 'minPrice', 'maxPrice', 'fields'];
  inputs.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.value = '';
    }
  });
  
  // Clear dropdowns
  const selects = ['category', 'perPage'];
  selects.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.selectedIndex = 0;
    }
  });
  
  // Clear price range error states
  const priceRangeContainer = document.querySelector('.price-range');
  if (priceRangeContainer) {
    priceRangeContainer.classList.remove('price-range-error');
    const existingError = priceRangeContainer.querySelector('.price-error-message');
    if (existingError) existingError.remove();
  }
  
  // Reset results to initial state
  const resultsContainer = document.getElementById('resultsContainer');
  resultsContainer.innerHTML = `
    <div class="empty-state-modern">
      <div class="empty-icon-modern">🔍</div>
      <h3 class="empty-title">Start Your Discovery Journey</h3>
      <p class="empty-description">Enter a search query above to explore our intelligent product database</p>
      <div class="search-suggestions">
        <p class="suggestions-title">Try searching for:</p>
        <div class="suggestion-tags">
          <span class="suggestion-tag" onclick="document.getElementById('searchQuery').value='gaming laptop'; document.getElementById('searchBtn').click();">gaming laptop</span>
          <span class="suggestion-tag" onclick="document.getElementById('searchQuery').value='wireless headphones'; document.getElementById('searchBtn').click();">wireless headphones</span>
          <span class="suggestion-tag" onclick="document.getElementById('searchQuery').value='smartphone under 20000'; document.getElementById('searchBtn').click();">smartphone under 20000</span>
        </div>
      </div>
    </div>
  `;
  
  // Clear pagination
  document.getElementById('pagination').innerHTML = '';
  
  // Reset pagination variables
  currentPage = 1;
  totalPages = 1;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  const searchBtn = document.getElementById('searchBtn');
  const searchQuery = document.getElementById('searchQuery');
  const minPrice = document.getElementById('minPrice');
  const maxPrice = document.getElementById('maxPrice');

  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      currentPage = 1;
      performSearch();
    });
  }

  if (searchQuery) {
    searchQuery.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        currentPage = 1;
        performSearch();
      }
    });
  }

  // Price range validation
  if (minPrice) {
    minPrice.addEventListener('input', validatePriceRangeRealtime);
    minPrice.addEventListener('blur', validatePriceRangeRealtime);
  }

  if (maxPrice) {
    maxPrice.addEventListener('input', validatePriceRangeRealtime);
    maxPrice.addEventListener('blur', validatePriceRangeRealtime);
  }

  // Clear filters button
  const clearFiltersBtn = document.querySelector('.clear-filters-btn');
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', clearFilters);
  }
});
