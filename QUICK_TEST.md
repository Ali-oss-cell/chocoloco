# 🚀 Quick Test - Copy & Paste Ready

Copy each mutation exactly as shown below into GraphiQL.

---

## ✅ Step 1: Create Category

```graphql
mutation {
  createCategory(input: {
    name: "Premium Chocolates"
    slug: "premium-chocolates"
    description: "Finest chocolate selection"
    isActive: true
    displayOrder: 1
  }) {
    success
    message
    category {
      id
      name
      slug
    }
  }
}
```

**Expected:** Category ID = 1

---

## ✅ Step 2: Create Brand

```graphql
mutation {
  createBrand(input: {
    name: "Lindt"
    slug: "lindt"
    description: "Swiss chocolate excellence"
    countryOfOrigin: "Switzerland"
    isActive: true
    displayOrder: 1
  }) {
    success
    message
    brand {
      id
      name
      countryOfOrigin
    }
  }
}
```

**Expected:** Brand ID = 1

---

## ✅ Step 3: Create Product

```graphql
mutation {
  createProduct(input: {
    sku: "LINDT-DARK-85"
    name: "Lindt Excellence Dark 85%"
    slug: "lindt-excellence-dark-85"
    brandId: 1
    categoryId: 1
    description: "Intense dark chocolate with 85% cocoa content"
    shortDescription: "Intense 85% dark chocolate"
    ingredients: "Cocoa mass, cocoa butter, sugar, vanilla"
    allergenInfo: "May contain traces of milk and nuts"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) {
    success
    message
    product {
      id
      sku
      name
      weight
      brand {
        name
      }
      category {
        name
      }
    }
  }
}
```

**Expected:** Product ID = 1

---

## ✅ Step 4: Set Retail Price

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "45.00"
    salePrice: "39.99"
    minQuantity: 1
    isActive: true
  }) {
    success
    message
    price {
      id
      priceType
      basePrice
      salePrice
      minQuantity
    }
  }
}
```

**Expected:** Price created successfully

---

## ✅ Step 5: Update Inventory

```graphql
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 500
    lowStockThreshold: 50
    warehouseLocation: "Warehouse A - Shelf 3"
  }) {
    success
    message
    inventory {
      quantityInStock
      lowStockThreshold
      warehouseLocation
      isInStock
    }
  }
}
```

**Expected:** 500 units in stock

---

## ✅ Step 6: Query Your Product

```graphql
query {
  product(id: 1) {
    id
    sku
    name
    description
    weight
    unitType
    isActive
    featured
    brand {
      name
      countryOfOrigin
    }
    category {
      name
    }
    prices {
      priceType
      basePrice
      salePrice
    }
    inventory {
      quantityInStock
      lowStockThreshold
      isInStock
    }
  }
}
```

**Expected:** Complete product with all details!

---

## ✅ Step 7: Test Search

```graphql
query {
  searchProducts(query: "lindt", limit: 5) {
    id
    name
    sku
    brand {
      name
    }
    prices {
      basePrice
      salePrice
    }
    inventory {
      quantityInStock
      isInStock
    }
  }
}
```

**Expected:** Should find your Lindt product!

---

## ✅ Step 8: Get All Products

```graphql
query {
  products {
    id
    name
    sku
    brand {
      name
    }
    category {
      name
    }
    prices {
      basePrice
      salePrice
    }
    inventory {
      quantityInStock
    }
  }
}
```

---

## 🎉 Success Checklist

After completing steps 1-6:

- ✅ Category "Premium Chocolates" created
- ✅ Brand "Lindt" created  
- ✅ Product "Lindt Excellence Dark 85%" created
- ✅ Retail price: AED 39.99 (sale) / AED 45.00 (regular)
- ✅ Stock: 500 units
- ✅ Search works
- ✅ Product is active and featured

---

## 🚀 Add More Products

Want to add more? Try this batch mutation:

```graphql
mutation {
  # Product 2
  product2: createProduct(input: {
    sku: "LINDT-MILK-001"
    name: "Lindt Milk Chocolate Classic"
    slug: "lindt-milk-chocolate-classic"
    brandId: 1
    categoryId: 1
    description: "Smooth and creamy milk chocolate"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) {
    success
    product { id name }
  }
  
  price2: setProductPrice(input: {
    productId: 2
    priceType: "RETAIL"
    basePrice: "35.00"
    minQuantity: 1
  }) {
    success
  }
  
  inventory2: updateInventory(input: {
    productId: 2
    quantityInStock: 300
  }) {
    success
  }
}
```

---

## 💡 Remember

- **Integers**: No quotes → `brandId: 1`
- **Decimals**: Use quotes → `price: "45.00"`
- **Strings**: Use quotes → `name: "Product"`
- **Booleans**: No quotes → `isActive: true`

---

**Start with Step 1 and work your way down!** 🎯

