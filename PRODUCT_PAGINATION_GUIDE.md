# Product Pagination & Organization Guide

## 📊 **HOW MANY PRODUCTS SHOW**

---

## **🎯 DEFAULT LIMITS**

| Page Type | Products Shown | Reason |
|-----------|----------------|---------|
| **Homepage** | 8-12 products | Fast loading, best products |
| **Category Page** | 12-20 products | More products, organized by category |
| **Search Results** | 10-15 products | Relevant results, not overwhelming |
| **Admin View** | 50-100 products | Management efficiency |

---

## **📄 PAGINATION SYSTEM**

### **How Pagination Works:**

```graphql
# Page 1 (First 8 products)
query {
  products(limit: 8, offset: 0) {
    id
    name
    retailPrice
  }
}

# Page 2 (Next 8 products)
query {
  products(limit: 8, offset: 8) {
    id
    name
    retailPrice
  }
}

# Page 3 (Next 8 products)
query {
  products(limit: 8, offset: 16) {
    id
    name
    retailPrice
  }
}
```

### **Pagination Calculation:**
- **Total Products:** 21
- **Products per Page:** 12
- **Total Pages:** 2
- **Page 1:** Products 1-12
- **Page 2:** Products 13-21

---

## **🔄 SORTING OPTIONS**

### **Available Sort Options:**

```graphql
# Sort by Name (A-Z)
products(sortBy: "name") { ... }

# Sort by Price (Low to High)
products(sortBy: "price_asc") { ... }

# Sort by Price (High to Low)
products(sortBy: "price_desc") { ... }

# Sort by Newest First
products(sortBy: "newest") { ... }

# Sort by Oldest First
products(sortBy: "oldest") { ... }

# Sort by Highest Rated
products(sortBy: "rating") { ... }
```

### **Sort Examples:**

**Name (A-Z):**
- Cadbury Dairy Milk Chocolate
- Coco Mass
- Ferrero Rocher Collection 16 pieces

**Price (Low to High):**
- Coco Mass - None AED
- Cadbury Dairy Milk Chocolate - 29.99 AED
- Toblerone Milk Chocolate - 38.00 AED

**Price (High to Low):**
- Ferrero Rocher Collection 24 pieces - 129.99 AED
- Godiva Chocolate Gift Box Assortment - 109.99 AED
- Lindt Swiss Luxury Selection - 84.99 AED

---

## **🏷️ CATEGORY ORGANIZATION**

### **Products are organized by:**

1. **Categories:**
   - Chocolate Bars
   - Dark Chocolate
   - Milk Chocolate
   - Premium Chocolates
   - Chocolate Ingredients

2. **Brands:**
   - Cadbury
   - Ferrero Rocher
   - Godiva
   - Lindt
   - Premium Cacao

3. **Product Types:**
   - Regular Products (single price)
   - Variant Products (multiple options)

---

## **📱 FRONTEND PAGINATION IMPLEMENTATION**

### **React Pagination Component:**

```javascript
import { useState } from 'react';
import { useQuery } from '@apollo/client';

const PRODUCTS_PER_PAGE = 12;

function ProductList() {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState('newest');
  
  const offset = (currentPage - 1) * PRODUCTS_PER_PAGE;
  
  const { data, loading } = useQuery(GET_PRODUCTS, {
    variables: {
      limit: PRODUCTS_PER_PAGE,
      offset: offset,
      sortBy: sortBy
    }
  });
  
  if (loading) return <div>Loading...</div>;
  
  const products = data?.products || [];
  const totalPages = Math.ceil(products.length / PRODUCTS_PER_PAGE);
  
  return (
    <div>
      {/* Sort Options */}
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="newest">Newest First</option>
        <option value="price_asc">Price: Low to High</option>
        <option value="price_desc">Price: High to Low</option>
        <option value="name">Name A-Z</option>
        <option value="rating">Highest Rated</option>
      </select>
      
      {/* Product Grid */}
      <div className="product-grid">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      
      {/* Pagination Controls */}
      <div className="pagination">
        <button 
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(currentPage - 1)}
        >
          Previous
        </button>
        
        <span>
          Page {currentPage} of {totalPages}
        </span>
        
        <button 
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(currentPage + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
```

### **Vue Pagination Component:**

```javascript
<template>
  <div>
    <!-- Sort Options -->
    <select v-model="sortBy" @change="loadProducts">
      <option value="newest">Newest First</option>
      <option value="price_asc">Price: Low to High</option>
      <option value="price_desc">Price: High to Low</option>
      <option value="name">Name A-Z</option>
      <option value="rating">Highest Rated</option>
    </select>
    
    <!-- Product Grid -->
    <div class="product-grid">
      <ProductCard 
        v-for="product in products" 
        :key="product.id" 
        :product="product" 
      />
    </div>
    
    <!-- Pagination Controls -->
    <div class="pagination">
      <button 
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        Previous
      </button>
      
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      
      <button 
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentPage: 1,
      sortBy: 'newest',
      products: [],
      totalPages: 1
    };
  },
  
  methods: {
    async loadProducts() {
      const offset = (this.currentPage - 1) * 12;
      
      const response = await fetch('http://localhost:8000/graphql/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `
            query {
              products(limit: 12, offset: ${offset}, sortBy: "${this.sortBy}") {
                id
                name
                retailPrice
                inStock
                images { image isPrimary }
              }
            }
          `
        })
      });
      
      const data = await response.json();
      this.products = data.data.products;
      this.totalPages = Math.ceil(this.products.length / 12);
    },
    
    goToPage(page) {
      this.currentPage = page;
      this.loadProducts();
    }
  },
  
  mounted() {
    this.loadProducts();
  }
};
</script>
```

---

## **🎨 PAGINATION CSS**

### **Pagination Styling:**

```css
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 20px 0;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.pagination button:hover:not(:disabled) {
  background: #f0f0f0;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  padding: 8px 16px;
  font-weight: bold;
}

/* Sort Dropdown */
.sort-select {
  margin-bottom: 20px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

/* Product Grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state h3 {
  margin-bottom: 10px;
}

.empty-state p {
  color: #999;
}
```

---

## **📊 RECOMMENDED SETTINGS**

### **Homepage:**
```graphql
query {
  products(limit: 8, sortBy: "newest") {
    id
    name
    retailPrice
    inStock
    images { image isPrimary }
  }
}
```

### **Category Page:**
```graphql
query {
  products(
    category: "chocolate-bars"
    limit: 12
    sortBy: "price_asc"
  ) {
    id
    name
    retailPrice
    inStock
  }
}
```

### **Search Results:**
```graphql
query {
  searchProducts(
    query: "chocolate"
    limit: 10
  ) {
    id
    name
    retailPrice
    inStock
  }
}
```

### **Admin View:**
```graphql
query {
  products(limit: 50, sortBy: "newest") {
    id
    name
    sku
    retailPrice
    inStock
    createdAt
  }
}
```

---

## **⚡ PERFORMANCE TIPS**

### **1. Limit Results:**
```graphql
# ✅ Good - limits data transfer
products(limit: 12) { ... }

# ❌ Bad - loads everything
products { ... }
```

### **2. Use Pagination:**
```graphql
# ✅ Good - paginated
products(limit: 12, offset: 24) { ... }

# ❌ Bad - loads all at once
products { ... }
```

### **3. Select Only Needed Fields:**
```graphql
# ✅ Good - only essential fields
products {
  id
  name
  retailPrice
  images { image isPrimary }
}

# ❌ Bad - loads everything
products {
  id
  name
  description
  ingredients
  nutritionalInfo
  # ... many more fields
}
```

---

## **🔄 LOADING STATES**

### **Loading Component:**

```javascript
function ProductList() {
  const { data, loading, error } = useQuery(GET_PRODUCTS);
  
  if (loading) {
    return (
      <div className="loading-grid">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="product-skeleton">
            <div className="skeleton-image"></div>
            <div className="skeleton-text"></div>
            <div className="skeleton-text short"></div>
            <div className="skeleton-button"></div>
          </div>
        ))}
      </div>
    );
  }
  
  if (error) {
    return <div className="error">Failed to load products</div>;
  }
  
  if (data.products.length === 0) {
    return (
      <div className="empty-state">
        <h3>No products found</h3>
        <p>Try adjusting your search or filters</p>
      </div>
    );
  }
  
  return (
    <div className="product-grid">
      {data.products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

---

## **📱 MOBILE PAGINATION**

### **Mobile-Friendly Pagination:**

```css
/* Mobile Pagination */
@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 10px;
  }
  
  .pagination button {
    width: 100%;
    padding: 12px;
  }
  
  .product-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }
}

/* Touch-Friendly Buttons */
.pagination button {
  min-height: 44px; /* iOS touch target */
  min-width: 44px;
}
```

---

## **✅ SUMMARY**

### **Your Product System:**

1. **Total Products:** 21 products
2. **Default Limit:** 12 products per page
3. **Total Pages:** 2 pages
4. **Sorting:** 6 different options
5. **Categories:** 5 categories
6. **Brands:** 5 brands

### **Recommended Setup:**

- **Homepage:** 8 products, newest first
- **Category Pages:** 12 products, price sorted
- **Search Results:** 10 products, relevance sorted
- **Admin View:** 50 products, newest first

### **Ready to Use:**

1. **Copy the queries** above
2. **Implement pagination** in your frontend
3. **Add sorting options** for users
4. **Style the pagination** controls
5. **Test on mobile** devices

**Your product system is fully organized and ready! 🎯✨**
