# 🔍 Search Implementation Guide

Complete guide for implementing search functionality in your chocolate e-commerce platform.

---

## 🎯 **What We Built**

A powerful search-as-you-type (autocomplete) feature that searches across:
- ✅ Product names
- ✅ Product SKUs
- ✅ Product descriptions
- ✅ Brand names
- ✅ Category names

**Features:**
- Fast results (optimized queries)
- Relevance sorting (matches starting with query appear first)
- Configurable result limit
- Minimum 2 characters required
- Returns full product details (price, stock, images)

---

## 📋 **GraphQL Query**

### **Search Products (Autocomplete)**

```graphql
query SearchProducts($query: String!, $limit: Int) {
  searchProducts(query: $query, limit: $limit) {
    id
    name
    sku
    slug
    retailPrice
    inStock
    brand {
      id
      name
      slug
    }
    category {
      id
      name
      slug
    }
    images {
      image
      isPrimary
    }
    inventory {
      availableQuantity
      isInStock
    }
  }
}
```

**Variables:**
```json
{
  "query": "chocolate",
  "limit": 10
}
```

---

## 🧪 **Testing in GraphiQL**

Open: **http://localhost:8000/graphql**

### **Example 1: Search for "chocolate"**

```graphql
query {
  searchProducts(query: "chocolate", limit: 5) {
    name
    sku
    retailPrice
    brand {
      name
    }
    inStock
  }
}
```

### **Example 2: Search for brand name "Lindt"**

```graphql
query {
  searchProducts(query: "Lindt", limit: 10) {
    name
    brand {
      name
    }
    retailPrice
    inStock
  }
}
```

### **Example 3: Search by SKU**

```graphql
query {
  searchProducts(query: "CHO-001") {
    name
    sku
    retailPrice
  }
}
```

### **Example 4: Full details for frontend**

```graphql
query {
  searchProducts(query: "dark", limit: 8) {
    id
    name
    slug
    retailPrice
    inStock
    brand {
      name
    }
    category {
      name
    }
    images {
      image
      isPrimary
    }
  }
}
```

---

## ⚛️ **React Frontend Implementation**

### **1. Install Apollo Client (if not already)**

```bash
npm install @apollo/client graphql
```

### **2. Create Search Hook**

Create: `hooks/useProductSearch.js`

```javascript
import { useState, useEffect } from 'react';
import { useLazyQuery, gql } from '@apollo/client';

const SEARCH_PRODUCTS = gql`
  query SearchProducts($query: String!, $limit: Int) {
    searchProducts(query: $query, limit: $limit) {
      id
      name
      slug
      retailPrice
      inStock
      brand {
        name
      }
      category {
        name
      }
      images {
        image
        isPrimary
      }
    }
  }
`;

export const useProductSearch = (debounceMs = 300) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  
  const [searchProducts, { data, loading, error }] = useLazyQuery(
    SEARCH_PRODUCTS,
    {
      fetchPolicy: 'network-only', // Always fetch fresh results
    }
  );

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchQuery, debounceMs]);

  // Trigger search when debounced query changes
  useEffect(() => {
    if (debouncedQuery && debouncedQuery.length >= 2) {
      searchProducts({
        variables: {
          query: debouncedQuery,
          limit: 10,
        },
      });
    }
  }, [debouncedQuery, searchProducts]);

  return {
    searchQuery,
    setSearchQuery,
    results: data?.searchProducts || [],
    loading,
    error,
  };
};
```

### **3. Search Input Component**

Create: `components/SearchBar.jsx`

```javascript
import React, { useState, useRef, useEffect } from 'react';
import { useProductSearch } from '../hooks/useProductSearch';
import { useNavigate } from 'react-router-dom';

const SearchBar = () => {
  const navigate = useNavigate();
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);
  
  const { 
    searchQuery, 
    setSearchQuery, 
    results, 
    loading 
  } = useProductSearch();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    setShowResults(query.length >= 2);
  };

  const handleProductClick = (product) => {
    navigate(`/product/${product.slug}`);
    setShowResults(false);
    setSearchQuery('');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.length >= 2) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
      setShowResults(false);
    }
  };

  return (
    <div ref={searchRef} className="search-container">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Search chocolates..."
          value={searchQuery}
          onChange={handleInputChange}
          onFocus={() => searchQuery.length >= 2 && setShowResults(true)}
          className="search-input"
        />
        <button type="submit" className="search-button">
          🔍 Search
        </button>
      </form>

      {/* Autocomplete Dropdown */}
      {showResults && (
        <div className="search-results-dropdown">
          {loading && (
            <div className="search-loading">Searching...</div>
          )}
          
          {!loading && results.length === 0 && (
            <div className="search-no-results">
              No products found for "{searchQuery}"
            </div>
          )}
          
          {!loading && results.length > 0 && (
            <ul className="search-results-list">
              {results.map((product) => (
                <li
                  key={product.id}
                  onClick={() => handleProductClick(product)}
                  className="search-result-item"
                >
                  <div className="result-image">
                    {product.images.find(img => img.isPrimary) ? (
                      <img
                        src={product.images.find(img => img.isPrimary).image}
                        alt={product.name}
                      />
                    ) : (
                      <div className="no-image">📦</div>
                    )}
                  </div>
                  
                  <div className="result-details">
                    <h4>{product.name}</h4>
                    <p className="result-brand">{product.brand.name}</p>
                    <p className="result-category">{product.category.name}</p>
                  </div>
                  
                  <div className="result-price">
                    <span className="price">{product.retailPrice} AED</span>
                    {product.inStock ? (
                      <span className="in-stock">✓ In Stock</span>
                    ) : (
                      <span className="out-of-stock">Out of Stock</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
```

### **4. CSS Styling**

Create: `styles/SearchBar.css`

```css
.search-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.search-form {
  display: flex;
  gap: 8px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #8B4513; /* Chocolate brown */
}

.search-button {
  padding: 12px 24px;
  background: #8B4513;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.search-button:hover {
  background: #654321;
}

/* Dropdown */
.search-results-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-top: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
}

.search-loading,
.search-no-results {
  padding: 16px;
  text-align: center;
  color: #666;
}

.search-results-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: #f9f9f9;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-image {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 24px;
}

.result-details {
  flex: 1;
}

.result-details h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.result-brand,
.result-category {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.result-price {
  text-align: right;
}

.price {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 4px;
}

.in-stock {
  display: block;
  font-size: 12px;
  color: #4CAF50;
}

.out-of-stock {
  display: block;
  font-size: 12px;
  color: #f44336;
}
```

### **5. Usage in App**

```javascript
import SearchBar from './components/SearchBar';

function HomePage() {
  return (
    <div className="home-page">
      <header>
        <h1>Chocolate Shop UAE 🍫</h1>
        <SearchBar />
      </header>
      
      {/* Rest of your homepage */}
    </div>
  );
}
```

---

## 🚀 **Advanced Features**

### **Option 1: Add Search Suggestions**

Modify the query to also return categories and brands:

```graphql
query SearchAll($query: String!) {
  searchProducts(query: $query, limit: 5) {
    id
    name
    slug
    retailPrice
  }
  
  categories(isActive: true) {
    id
    name
    slug
  }
  
  brands(isActive: true) {
    id
    name
    slug
  }
}
```

### **Option 2: Search History**

Store recent searches in localStorage:

```javascript
const saveSearchHistory = (query) => {
  const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
  const newHistory = [query, ...history.filter(q => q !== query)].slice(0, 10);
  localStorage.setItem('searchHistory', JSON.stringify(newHistory));
};
```

### **Option 3: Popular Searches**

Add a query for trending products:

```graphql
query {
  products(featured: true, limit: 5) {
    name
    slug
  }
}
```

---

## ⚡ **Performance Tips**

### **1. Debouncing (Already Implemented)**
- Waits 300ms after user stops typing
- Reduces API calls significantly

### **2. Caching**
```javascript
const [searchProducts] = useLazyQuery(SEARCH_PRODUCTS, {
  fetchPolicy: 'cache-first', // Use cached results
});
```

### **3. Backend Optimization**
The search query is already optimized with:
- `select_related()` - Reduces database queries
- `prefetch_related()` - Efficient loading of related data
- Result limiting - Fast response times
- Indexed fields (name, slug, sku)

---

## 📱 **Mobile Optimization**

```css
@media (max-width: 768px) {
  .search-container {
    max-width: 100%;
  }
  
  .search-form {
    flex-direction: column;
  }
  
  .search-button {
    width: 100%;
  }
  
  .search-results-dropdown {
    max-height: 60vh;
  }
  
  .search-result-item {
    flex-direction: column;
    text-align: center;
  }
}
```

---

## 🧪 **Testing Checklist**

- [ ] Search returns results for product names
- [ ] Search returns results for brand names
- [ ] Search returns results for category names
- [ ] Search returns results for SKUs
- [ ] Minimum 2 characters required
- [ ] Results sorted by relevance
- [ ] Fast response time (<200ms)
- [ ] Debouncing works (no excessive API calls)
- [ ] Dropdown closes when clicking outside
- [ ] Mobile responsive
- [ ] Stock status displays correctly
- [ ] Prices display correctly

---

## 🎯 **User Experience Tips**

### **1. Show Loading State**
```javascript
{loading && <div className="search-spinner">🔄 Searching...</div>}
```

### **2. Show "No Results" Message**
```javascript
{!loading && results.length === 0 && query.length >= 2 && (
  <div>
    No results for "{query}". Try:
    <ul>
      <li>Different keywords</li>
      <li>Brand names (Lindt, Ferrero, etc.)</li>
      <li>Product categories (Dark Chocolate, Truffles, etc.)</li>
    </ul>
  </div>
)}
```

### **3. Highlight Search Terms**
```javascript
const highlightMatch = (text, query) => {
  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return parts.map((part, i) => 
    part.toLowerCase() === query.toLowerCase() ? 
      <mark key={i}>{part}</mark> : part
  );
};
```

### **4. Keyboard Navigation**
Add arrow key navigation in the dropdown:
```javascript
const handleKeyDown = (e) => {
  if (e.key === 'ArrowDown') {
    // Navigate to next result
  } else if (e.key === 'ArrowUp') {
    // Navigate to previous result
  } else if (e.key === 'Enter') {
    // Select highlighted result
  }
};
```

---

## 📊 **Analytics Integration**

Track search analytics:

```javascript
const trackSearch = (query, resultsCount) => {
  // Google Analytics
  gtag('event', 'search', {
    search_term: query,
    results_count: resultsCount
  });
  
  // Or your analytics service
  analytics.track('Product Search', {
    query,
    resultsCount,
    timestamp: new Date()
  });
};
```

---

## ✅ **Summary**

You now have:
- ✅ Fast search-as-you-type API
- ✅ Searches across products, brands, categories, SKUs
- ✅ Relevance-based sorting
- ✅ Optimized database queries
- ✅ React component with debouncing
- ✅ Beautiful dropdown UI
- ✅ Mobile responsive

**Test it now:** http://localhost:8000/graphql

Try query:
```graphql
query {
  searchProducts(query: "chocolate") {
    name
    brand { name }
    retailPrice
  }
}
```

Your search is production-ready! 🎉

