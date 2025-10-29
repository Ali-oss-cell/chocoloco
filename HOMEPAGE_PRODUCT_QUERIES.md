# Homepage Product Queries - Complete Guide

## 🏠 **BEST QUERIES FOR YOUR WEBSITE'S FIRST PAGE**

---

## **🎯 RECOMMENDED: Simple Homepage Query**

**Use this for your main homepage/product catalog:**

```graphql
query GetHomepageProducts {
  products(limit: 8) {
    id
    name
    sku
    retailPrice
    inStock
    hasVariants
    images {
      image
      isPrimary
    }
    brand {
      name
    }
    category {
      name
    }
  }
}
```

**Why this is perfect:**
- ✅ Fast loading (only essential data)
- ✅ Shows all product types (regular + variants)
- ✅ Includes images for display
- ✅ Shows stock status
- ✅ Includes brand and category info
- ✅ Limited to 8 products (good for homepage)

---

## **🔥 FEATURED PRODUCTS QUERY**

**For highlighting special products:**

```graphql
query GetFeaturedProducts {
  products(featured: true, limit: 6) {
    id
    name
    retailPrice
    inStock
    images {
      image
      isPrimary
    }
    brand {
      name
    }
  }
}
```

**Use cases:**
- Homepage hero section
- "Featured Products" section
- Special promotions

---

## **📱 MOBILE-OPTIMIZED QUERY**

**For mobile apps or fast loading:**

```graphql
query GetMobileProducts {
  products(limit: 6) {
    id
    name
    retailPrice
    inStock
    images {
      image
      isPrimary
    }
  }
}
```

**Why this is good for mobile:**
- ✅ Minimal data transfer
- ✅ Only essential fields
- ✅ Fast loading
- ✅ Good for mobile networks

---

## **🛍️ ADVANCED: Products with Variants**

**For products that need variant display:**

```graphql
query GetProductsWithVariants {
  products(limit: 4) {
    id
    name
    retailPrice
    hasVariants
    variants {
      id
      sku
      price
      effectivePrice
      isInStock
      optionValues {
        value
      }
    }
    images {
      image
      isPrimary
    }
  }
}
```

**When to use:**
- Product detail pages
- When you need to show variant options
- Advanced product catalogs

---

## **🏷️ CATEGORY-BASED QUERIES**

**For category pages:**

```graphql
query GetCategoryProducts($categorySlug: String!) {
  products(category: $categorySlug, limit: 12) {
    id
    name
    retailPrice
    inStock
    images {
      image
      isPrimary
    }
    brand {
      name
    }
  }
}
```

**Category slugs you can use:**
- `"chocolate-bars"`
- `"dark-chocolate"`
- `"milk-chocolate"`
- `"premium-chocolates"`
- `"chocolate-ingredients"`

---

## **🔍 SEARCH QUERIES**

**For search functionality:**

```graphql
query SearchProducts($query: String!) {
  searchProducts(query: $query, limit: 10) {
    id
    name
    retailPrice
    inStock
    images {
      image
      isPrimary
    }
    brand {
      name
    }
  }
}
```

**Advanced search with fuzzy matching:**

```graphql
query FuzzySearchProducts($query: String!) {
  fuzzySearchProducts(query: $query, limit: 10) {
    id
    name
    retailPrice
    inStock
    images {
      image
      isPrimary
    }
  }
}
```

---

## **📊 FRONTEND IMPLEMENTATION**

### **React Example:**

```javascript
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';

const GET_HOMEPAGE_PRODUCTS = gql`
  query GetHomepageProducts {
    products(limit: 8) {
      id
      name
      retailPrice
      inStock
      hasVariants
      images {
        image
        isPrimary
      }
      brand {
        name
      }
      category {
        name
      }
    }
  }
`;

function Homepage() {
  const { loading, error, data } = useQuery(GET_HOMEPAGE_PRODUCTS);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div className="product-grid">
      {data.products.map(product => (
        <ProductCard 
          key={product.id}
          product={product}
        />
      ))}
    </div>
  );
}
```

### **Vue Example:**

```javascript
import { useQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client';

const GET_HOMEPAGE_PRODUCTS = gql`
  query GetHomepageProducts {
    products(limit: 8) {
      id
      name
      retailPrice
      inStock
      hasVariants
      images {
        image
        isPrimary
      }
    }
  }
`;

export default {
  setup() {
    const { result, loading, error } = useQuery(GET_HOMEPAGE_PRODUCTS);
    
    return {
      products: result,
      loading,
      error
    };
  }
};
```

### **Vanilla JavaScript:**

```javascript
async function getHomepageProducts() {
  const response = await fetch('http://localhost:8000/graphql/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: `
        query {
          products(limit: 8) {
            id
            name
            retailPrice
            inStock
            hasVariants
            images {
              image
              isPrimary
            }
            brand {
              name
            }
          }
        }
      `
    })
  });
  
  const data = await response.json();
  return data.data.products;
}

// Usage
getHomepageProducts().then(products => {
  console.log('Products:', products);
  // Render your products here
});
```

---

## **🎨 PRODUCT CARD COMPONENT**

### **React Product Card:**

```javascript
function ProductCard({ product }) {
  const primaryImage = product.images.find(img => img.isPrimary)?.image;
  
  return (
    <div className="product-card">
      {primaryImage && (
        <img 
          src={primaryImage} 
          alt={product.name}
          className="product-image"
        />
      )}
      
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-brand">{product.brand.name}</p>
        <p className="product-category">{product.category.name}</p>
        
        <div className="product-price">
          <span className="price">{product.retailPrice} AED</span>
          {!product.inStock && (
            <span className="out-of-stock">Out of Stock</span>
          )}
        </div>
        
        {product.hasVariants && (
          <p className="has-variants">Multiple options available</p>
        )}
        
        <button 
          className="add-to-cart-btn"
          disabled={!product.inStock}
        >
          {product.inStock ? 'Add to Cart' : 'Out of Stock'}
        </button>
      </div>
    </div>
  );
}
```

---

## **📱 RESPONSIVE DESIGN**

### **CSS Grid Layout:**

```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 20px;
}

.product-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 1.1rem;
  margin: 0 0 8px 0;
  color: #333;
}

.product-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #e74c3c;
  margin: 10px 0;
}

.add-to-cart-btn {
  width: 100%;
  padding: 10px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-to-cart-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}
```

---

## **⚡ PERFORMANCE OPTIMIZATION**

### **1. Limit Results:**
```graphql
# Good - limits data transfer
products(limit: 8) { ... }

# Bad - loads everything
products { ... }
```

### **2. Select Only Needed Fields:**
```graphql
# Good - only essential fields
products {
  id
  name
  retailPrice
  images { image isPrimary }
}

# Bad - loads everything
products {
  id
  name
  description
  ingredients
  nutritionalInfo
  # ... many more fields
}
```

### **3. Use Images Efficiently:**
```graphql
# Good - only primary image
images {
  image
  isPrimary
}

# Bad - loads all images
images {
  image
  altText
  displayOrder
  # ... more fields
}
```

---

## **🔄 LOADING STATES**

### **React Loading Component:**

```javascript
function ProductGrid() {
  const { loading, error, data } = useQuery(GET_HOMEPAGE_PRODUCTS);
  
  if (loading) {
    return (
      <div className="loading-grid">
        {[...Array(8)].map((_, i) => (
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
  
  return (
    <div className="product-grid">
      {data.products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### **Skeleton CSS:**

```css
.product-skeleton {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
}

.skeleton-image {
  width: 100%;
  height: 200px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 15px;
}

.skeleton-text {
  height: 20px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 10px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-button {
  height: 40px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-top: 15px;
}
```

---

## **📊 QUERY COMPARISON**

| Query Type | Use Case | Data Size | Speed |
|------------|----------|-----------|-------|
| Simple | Homepage | Small | Fast |
| Featured | Hero section | Small | Fast |
| With Variants | Product pages | Medium | Medium |
| Search | Search results | Medium | Medium |
| Category | Category pages | Medium | Medium |

---

## **🎯 RECOMMENDATIONS**

### **For Homepage:**
```graphql
# ✅ BEST CHOICE
products(limit: 8) {
  id
  name
  retailPrice
  inStock
  hasVariants
  images { image isPrimary }
  brand { name }
}
```

### **For Category Pages:**
```graphql
# ✅ BEST CHOICE
products(category: "chocolate-bars", limit: 12) {
  id
  name
  retailPrice
  inStock
  images { image isPrimary }
}
```

### **For Search:**
```graphql
# ✅ BEST CHOICE
searchProducts(query: "chocolate", limit: 10) {
  id
  name
  retailPrice
  inStock
  images { image isPrimary }
}
```

---

## **✅ SUMMARY**

**Your homepage should use:**
1. **Simple query** with essential fields only
2. **Limit to 6-8 products** for fast loading
3. **Include images** for visual appeal
4. **Show stock status** for user experience
5. **Include brand/category** for context

**This gives you the perfect balance of:**
- ✅ Fast loading
- ✅ Good user experience
- ✅ Essential information
- ✅ Mobile-friendly
- ✅ SEO-friendly

**Ready to build your homepage! 🏠✨**
