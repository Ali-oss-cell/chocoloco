# 🔍 Frontend Search Integration Guide

Complete guide for implementing search functionality in your frontend application.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Search Types Available](#search-types-available)
3. [GraphQL Queries](#graphql-queries)
4. [How Search Works](#how-search-works)
5. [Frontend Implementation](#frontend-implementation)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)

---

## 🎯 Overview

Your backend provides **3 types of search**:

1. **Fast Search** (`searchProducts`) - For autocomplete/search-as-you-type
2. **Fuzzy Search** (`fuzzySearchProducts`) - Handles typos and misspellings
3. **Search Suggestions** (`searchSuggestions`) - Smart suggestions as user types

**All searches are:**
- ✅ Public (no authentication required)
- ✅ Fast and optimized
- ✅ Search across multiple fields
- ✅ Minimum 2 characters required

---

## 🔍 Search Types Available

### 1. Fast Search (`searchProducts`)

**Best for:** Autocomplete, search-as-you-type, instant results

**Features:**
- Searches: Product name, SKU, description, brand name, category name
- Results sorted by relevance (name matches first)
- Fast response time
- Configurable limit (default: 10)

**Use when:**
- User is typing in search box
- Need instant results
- Want exact or partial matches

---

### 2. Fuzzy Search (`fuzzySearchProducts`)

**Best for:** Handling typos, misspellings, approximate matches

**Features:**
- Handles typos and misspellings
- Uses similarity matching
- Searches all product fields
- Configurable typo tolerance (default: 2 characters)

**Use when:**
- User might make spelling mistakes
- Want to find products even with typos
- Need more flexible matching

---

### 3. Search Suggestions (`searchSuggestions`)

**Best for:** Autocomplete dropdown, search hints

**Features:**
- Returns suggested search terms
- Based on product names, brands, categories
- Helps users find what they're looking for
- Popular terms included

**Use when:**
- Building autocomplete dropdown
- Want to suggest popular searches
- Help users discover products

---

## 📝 GraphQL Queries

### 1. Fast Search Query

```graphql
query SearchProducts($query: String!, $limit: Int, $sortBy: String) {
  searchProducts(query: $query, limit: $limit, sortBy: $sortBy) {
    id
    name
    sku
    slug
    description
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
  "limit": 10,
  "sortBy": "name"
}
```

**Sort Options:**
- `name` - Alphabetical by name
- `price_asc` - Price low to high
- `price_desc` - Price high to low
- `rating` - By average rating
- `newest` - Newest first
- `oldest` - Oldest first
- (default) - Relevance (name matches first)

---

### 2. Fuzzy Search Query

```graphql
query FuzzySearchProducts(
  $query: String!
  $limit: Int
  $typoTolerance: Int
  $sortBy: String
) {
  fuzzySearchProducts(
    query: $query
    limit: $limit
    typoTolerance: $typoTolerance
    sortBy: $sortBy
  ) {
    id
    name
    sku
    slug
    retailPrice
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

**Variables:**
```json
{
  "query": "choclate",  // Note: typo in "chocolate"
  "limit": 10,
  "typoTolerance": 2,
  "sortBy": "name"
}
```

**Typo Tolerance:**
- `1` - Very strict (1 character difference)
- `2` - Default (2 character differences)
- `3` - More lenient (3 character differences)

---

### 3. Search Suggestions Query

```graphql
query SearchSuggestions($query: String!, $limit: Int) {
  searchSuggestions(query: $query, limit: $limit)
}
```

**Variables:**
```json
{
  "query": "choc",
  "limit": 5
}
```

**Response:**
```json
{
  "data": {
    "searchSuggestions": [
      "chocolate",
      "dark chocolate",
      "milk chocolate",
      "white chocolate",
      "chocolate gift box"
    ]
  }
}
```

---

### 4. Products with Search Filter

You can also use the `products` query with a `search` parameter:

```graphql
query ProductsWithSearch($search: String, $category: String, $brand: String) {
  products(search: $search, category: $category, brand: $brand, limit: 20) {
    id
    name
    sku
    retailPrice
    brand {
      name
    }
    category {
      name
    }
  }
}
```

**Variables:**
```json
{
  "search": "lindt",
  "category": "dark-chocolate",
  "brand": null
}
```

---

## 🔧 How Search Works

### Fast Search Algorithm

1. **User types:** "chocolate"
2. **Backend searches in:**
   - Product name (contains "chocolate")
   - Product SKU (contains "chocolate")
   - Product description (contains "chocolate")
   - Brand name (contains "chocolate")
   - Category name (contains "chocolate")
3. **Results sorted by:**
   - Products where name **starts with** "chocolate" (priority 0)
   - Products where name **contains** "chocolate" (priority 1)
4. **Returns:** Top 10 results (or specified limit)

### Fuzzy Search Algorithm

1. **User types:** "choclate" (typo)
2. **Backend:**
   - Gets all products
   - Calculates similarity score for each product
   - Compares query against: name, SKU, brand, category, description
   - Uses Levenshtein distance algorithm
3. **Results:**
   - Products with similarity ≥ 0.3 (for short queries)
   - Products with similarity ≥ 0.4 (for longer queries)
4. **Returns:** Top results sorted by similarity score

### Search Suggestions Algorithm

1. **User types:** "choc"
2. **Backend:**
   - Gets all product names, brand names, category names
   - Finds close matches using `difflib.get_close_matches`
   - If no matches, suggests popular terms
3. **Returns:** List of suggested search terms

---

## 💻 Frontend Implementation

### React/Next.js Example

```javascript
// hooks/useSearch.js
import { useState, useEffect } from 'react';
import { useLazyQuery } from '@apollo/client';
import { gql } from '@apollo/client';

const SEARCH_PRODUCTS = gql`
  query SearchProducts($query: String!, $limit: Int) {
    searchProducts(query: $query, limit: $limit) {
      id
      name
      sku
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

const SEARCH_SUGGESTIONS = gql`
  query SearchSuggestions($query: String!, $limit: Int) {
    searchSuggestions(query: $query, limit: $limit)
  }
`;

export function useSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchProducts, { data, loading, error }] = useLazyQuery(SEARCH_PRODUCTS);
  const [getSuggestions, { data: suggestionsData }] = useLazyQuery(SEARCH_SUGGESTIONS);

  // Debounce search
  useEffect(() => {
    if (searchQuery.length < 2) {
      return;
    }

    const timer = setTimeout(() => {
      searchProducts({
        variables: {
          query: searchQuery,
          limit: 10,
        },
      });
    }, 300); // Wait 300ms after user stops typing

    return () => clearTimeout(timer);
  }, [searchQuery, searchProducts]);

  // Get suggestions as user types
  useEffect(() => {
    if (searchQuery.length >= 2) {
      getSuggestions({
        variables: {
          query: searchQuery,
          limit: 5,
        },
      });
    }
  }, [searchQuery, getSuggestions]);

  return {
    searchQuery,
    setSearchQuery,
    results: data?.searchProducts || [],
    suggestions: suggestionsData?.searchSuggestions || [],
    loading,
    error,
  };
}

// components/SearchBar.jsx
import { useState } from 'react';
import { useSearch } from '../hooks/useSearch';
import { useRouter } from 'next/router';

export default function SearchBar() {
  const { searchQuery, setSearchQuery, results, suggestions, loading } = useSearch();
  const [showResults, setShowResults] = useState(false);
  const router = useRouter();

  const handleSearch = (query) => {
    setSearchQuery(query);
    setShowResults(true);
  };

  const handleSelectProduct = (product) => {
    router.push(`/products/${product.slug}`);
    setShowResults(false);
  };

  const handleSelectSuggestion = (suggestion) => {
    setSearchQuery(suggestion);
    setShowResults(true);
  };

  return (
    <div className="search-container">
      <div className="search-input-wrapper">
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => setShowResults(true)}
          className="search-input"
        />
        {loading && <span className="loading-spinner">⏳</span>}
      </div>

      {showResults && (results.length > 0 || suggestions.length > 0) && (
        <div className="search-results">
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="suggestions">
              <div className="suggestions-title">Suggestions:</div>
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleSelectSuggestion(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <div className="results">
              <div className="results-title">
                {results.length} result{results.length !== 1 ? 's' : ''} found
              </div>
              {results.map((product) => (
                <div
                  key={product.id}
                  className="result-item"
                  onClick={() => handleSelectProduct(product)}
                >
                  {product.images?.find((img) => img.isPrimary) && (
                    <img
                      src={product.images.find((img) => img.isPrimary).image}
                      alt={product.name}
                      className="result-image"
                    />
                  )}
                  <div className="result-info">
                    <div className="result-name">{product.name}</div>
                    <div className="result-brand">{product.brand?.name}</div>
                    <div className="result-price">AED {product.retailPrice}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {results.length === 0 && searchQuery.length >= 2 && !loading && (
            <div className="no-results">No products found</div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

### Vue.js Example

```vue
<template>
  <div class="search-container">
    <input
      v-model="searchQuery"
      @input="handleSearch"
      @focus="showResults = true"
      type="text"
      placeholder="Search products..."
      class="search-input"
    />
    
    <div v-if="showResults && (results.length > 0 || suggestions.length > 0)" class="search-results">
      <!-- Suggestions -->
      <div v-if="suggestions.length > 0" class="suggestions">
        <div class="suggestions-title">Suggestions:</div>
        <div
          v-for="(suggestion, index) in suggestions"
          :key="index"
          class="suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion }}
        </div>
      </div>

      <!-- Results -->
      <div v-if="results.length > 0" class="results">
        <div class="results-title">{{ results.length }} results found</div>
        <div
          v-for="product in results"
          :key="product.id"
          class="result-item"
          @click="selectProduct(product)"
        >
          <img
            v-if="product.images?.find(img => img.isPrimary)"
            :src="product.images.find(img => img.isPrimary).image"
            :alt="product.name"
            class="result-image"
          />
          <div class="result-info">
            <div class="result-name">{{ product.name }}</div>
            <div class="result-brand">{{ product.brand?.name }}</div>
            <div class="result-price">AED {{ product.retailPrice }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { useLazyQuery } from '@vue/apollo-composable';
import { gql } from '@apollo/client/core';

const SEARCH_PRODUCTS = gql`
  query SearchProducts($query: String!, $limit: Int) {
    searchProducts(query: $query, limit: $limit) {
      id
      name
      sku
      slug
      retailPrice
      brand {
        name
      }
      images {
        image
        isPrimary
      }
    }
  }
`;

const SEARCH_SUGGESTIONS = gql`
  query SearchSuggestions($query: String!, $limit: Int) {
    searchSuggestions(query: $query, limit: $limit)
  }
`;

export default {
  name: 'SearchBar',
  setup() {
    const searchQuery = ref('');
    const showResults = ref(false);
    const { result: searchResult, load: searchProducts, loading } = useLazyQuery(SEARCH_PRODUCTS);
    const { result: suggestionsResult, load: getSuggestions } = useLazyQuery(SEARCH_SUGGESTIONS);

    const results = computed(() => searchResult.value?.searchProducts || []);
    const suggestions = computed(() => suggestionsResult.value?.searchSuggestions || []);

    let searchTimer = null;

    const handleSearch = () => {
      if (searchQuery.value.length < 2) {
        return;
      }

      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        searchProducts({ query: searchQuery.value, limit: 10 });
        getSuggestions({ query: searchQuery.value, limit: 5 });
      }, 300);
    };

    const selectProduct = (product) => {
      // Navigate to product page
      router.push(`/products/${product.slug}`);
      showResults.value = false;
    };

    const selectSuggestion = (suggestion) => {
      searchQuery.value = suggestion;
      showResults.value = true;
    };

    return {
      searchQuery,
      showResults,
      results,
      suggestions,
      loading,
      handleSearch,
      selectProduct,
      selectSuggestion,
    };
  },
};
</script>
```

---

## 🎨 Complete Search Page Example

```javascript
// pages/search.jsx (Next.js) or SearchPage.jsx (React)
import { useState, useEffect } from 'react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import { useRouter } from 'next/router';

const SEARCH_PRODUCTS = gql`
  query SearchProducts($query: String!, $limit: Int, $sortBy: String) {
    searchProducts(query: $query, limit: $limit, sortBy: $sortBy) {
      id
      name
      sku
      slug
      description
      retailPrice
      inStock
      brand {
        name
        slug
      }
      category {
        name
        slug
      }
      images {
        image
        isPrimary
      }
    }
  }
`;

export default function SearchPage() {
  const router = useRouter();
  const { q, sort } = router.query;
  const [searchQuery, setSearchQuery] = useState(q || '');
  const [sortBy, setSortBy] = useState(sort || 'name');

  const { data, loading, error } = useQuery(SEARCH_PRODUCTS, {
    variables: {
      query: searchQuery,
      limit: 50,
      sortBy: sortBy,
    },
    skip: !searchQuery || searchQuery.length < 2,
  });

  const handleSearch = (e) => {
    e.preventDefault();
    router.push({
      pathname: '/search',
      query: { q: searchQuery, sort: sortBy },
    });
  };

  const results = data?.searchProducts || [];

  return (
    <div className="search-page">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search products..."
          className="search-input"
        />
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="name">Name</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="newest">Newest</option>
        </select>
        <button type="submit">Search</button>
      </form>

      {loading && <div>Searching...</div>}
      {error && <div>Error: {error.message}</div>}

      {results.length > 0 && (
        <div className="results">
          <h2>{results.length} results for "{searchQuery}"</h2>
          <div className="product-grid">
            {results.map((product) => (
              <div
                key={product.id}
                className="product-card"
                onClick={() => router.push(`/products/${product.slug}`)}
              >
                {product.images?.find((img) => img.isPrimary) && (
                  <img
                    src={product.images.find((img) => img.isPrimary).image}
                    alt={product.name}
                  />
                )}
                <h3>{product.name}</h3>
                <p>{product.brand?.name}</p>
                <p className="price">AED {product.retailPrice}</p>
                {!product.inStock && <span className="out-of-stock">Out of Stock</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && searchQuery.length >= 2 && results.length === 0 && (
        <div className="no-results">
          <h2>No products found for "{searchQuery}"</h2>
          <p>Try different keywords or check spelling</p>
        </div>
      )}
    </div>
  );
}
```

---

## ✅ Best Practices

### 1. Debounce Search Queries

Don't search on every keystroke. Wait 300-500ms after user stops typing:

```javascript
useEffect(() => {
  if (query.length < 2) return;
  
  const timer = setTimeout(() => {
    searchProducts({ variables: { query } });
  }, 300);
  
  return () => clearTimeout(timer);
}, [query]);
```

### 2. Minimum Character Requirement

Require at least 2 characters before searching:

```javascript
if (searchQuery.length < 2) {
  return; // Don't search
}
```

### 3. Show Loading States

Always show loading indicators:

```javascript
{loading && <div>Searching...</div>}
```

### 4. Handle Empty Results

Show helpful message when no results:

```javascript
{!loading && results.length === 0 && (
  <div>No products found. Try different keywords.</div>
)}
```

### 5. Cache Search Results

Use Apollo Client cache to avoid redundant queries:

```javascript
const { data } = useQuery(SEARCH_PRODUCTS, {
  variables: { query: searchQuery },
  fetchPolicy: 'cache-first', // Use cache if available
});
```

### 6. Keyboard Navigation

Add keyboard support for better UX:

```javascript
const handleKeyDown = (e) => {
  if (e.key === 'ArrowDown') {
    // Navigate to next result
  } else if (e.key === 'ArrowUp') {
    // Navigate to previous result
  } else if (e.key === 'Enter') {
    // Select current result
  }
};
```

### 7. Highlight Search Terms

Highlight matching text in results:

```javascript
const highlightText = (text, query) => {
  const regex = new RegExp(`(${query})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};
```

---

## 🧪 Testing Examples

### Test Fast Search

```graphql
query {
  searchProducts(query: "lindt", limit: 5) {
    name
    brand {
      name
    }
  }
}
```

### Test Fuzzy Search

```graphql
query {
  fuzzySearchProducts(query: "choclate", limit: 5) {
    name
  }
}
```

### Test Search Suggestions

```graphql
query {
  searchSuggestions(query: "choc", limit: 5)
}
```

---

## 📊 Search Fields

**Fast Search searches in:**
- ✅ Product name
- ✅ Product SKU
- ✅ Product description
- ✅ Brand name
- ✅ Category name

**Fuzzy Search searches in:**
- ✅ All of the above
- ✅ Handles typos and misspellings
- ✅ Ranks by similarity

---

## 🎯 Quick Reference

**GraphQL Endpoint:** `http://164.90.215.173/graphql/`

**Minimum Query Length:** 2 characters

**Default Limit:** 10 results

**Sort Options:**
- `name` - Alphabetical
- `price_asc` - Price low to high
- `price_desc` - Price high to low
- `rating` - By rating
- `newest` - Newest first
- `oldest` - Oldest first
- (default) - Relevance

---

**Ready to implement search!** 🔍

Start with the `searchProducts` query for autocomplete, then add `searchSuggestions` for better UX!

