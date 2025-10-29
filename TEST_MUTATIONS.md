# 🧪 Test Mutations - Step by Step

Copy and paste these into GraphiQL: `http://localhost:8000/graphql/`

---

## ✅ Step 1: Create Category

```graphql
mutation {
  createCategory(input: {
    name: "Premium Chocolates"
    slug: "premium-chocolates"
    description: "Finest chocolate selection from around the world"
    isActive: true
    displayOrder: 1
  }) {
    success
    message
    category {
      id
      name
      slug
      isActive
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "createCategory": {
      "success": true,
      "message": "Category 'Premium Chocolates' created successfully",
      "category": {
        "id": "1",
        "name": "Premium Chocolates",
        "slug": "premium-chocolates",
        "isActive": true
      }
    }
  }
}
```

✅ **Save the category ID** (should be 1)

---

## ✅ Step 2: Create Brand

```graphql
mutation {
  createBrand(input: {
    name: "Lindt"
    slug: "lindt"
    description: "Swiss chocolate excellence since 1845"
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
      isActive
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "createBrand": {
      "success": true,
      "message": "Brand 'Lindt' created successfully",
      "brand": {
        "id": "1",
        "name": "Lindt",
        "countryOfOrigin": "Switzerland",
        "isActive": true
      }
    }
  }
}
```

✅ **Save the brand ID** (should be 1)

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
    description: "Intense dark chocolate with 85% cocoa content. Perfect for dark chocolate lovers."
    shortDescription: "Intense 85% dark chocolate"
    ingredients: "Cocoa mass, cocoa butter, sugar, vanilla"
    allergenInfo: "May contain traces of milk and nuts"
    weight: 100.0
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
      brand {
        name
      }
      category {
        name
      }
      isActive
      featured
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "createProduct": {
      "success": true,
      "message": "Product 'Lindt Excellence Dark 85%' created successfully",
      "product": {
        "id": "1",
        "sku": "LINDT-DARK-85",
        "name": "Lindt Excellence Dark 85%",
        "brand": {
          "name": "Lindt"
        },
        "category": {
          "name": "Premium Chocolates"
        },
        "isActive": true,
        "featured": true
      }
    }
  }
}
```

✅ **Save the product ID** (should be 1)

---

## ✅ Step 4: Set Retail Price

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: 45.00
    salePrice: 39.99
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
      isActive
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "setProductPrice": {
      "success": true,
      "message": "Price created for 'Lindt Excellence Dark 85%'",
      "price": {
        "id": "1",
        "priceType": "RETAIL",
        "basePrice": "45.00",
        "salePrice": "39.99",
        "minQuantity": 1,
        "isActive": true
      }
    }
  }
}
```

---

## ✅ Step 5: Update Inventory

```graphql
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 500
    lowStockThreshold: 50
    warehouseLocation: "Warehouse A - Section 1 - Shelf 3"
  }) {
    success
    message
    inventory {
      id
      quantityInStock
      lowStockThreshold
      warehouseLocation
      isInStock
    }
  }
}
```

**Expected Response:**
```json
{
  "data": {
    "updateInventory": {
      "success": true,
      "message": "Inventory updated for 'Lindt Excellence Dark 85%': 500 units",
      "inventory": {
        "id": "1",
        "quantityInStock": 500,
        "lowStockThreshold": 50,
        "warehouseLocation": "Warehouse A - Section 1 - Shelf 3",
        "isInStock": true
      }
    }
  }
}
```

---

## ✅ Step 6: Query Your Product

Now let's see the complete product:

```graphql
query {
  product(id: 1) {
    id
    sku
    name
    slug
    description
    shortDescription
    ingredients
    allergenInfo
    weight
    unitType
    isActive
    featured
    brand {
      id
      name
      countryOfOrigin
    }
    category {
      id
      name
    }
    prices {
      id
      priceType
      basePrice
      salePrice
      minQuantity
    }
    inventory {
      quantityInStock
      lowStockThreshold
      warehouseLocation
      isInStock
    }
  }
}
```

**Expected Response:** Full product with all details!

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

**Expected Response:** Should find your Lindt product!

---

## 🎉 Step 8: Add More Products

Now add a few more products to test better. Here's a quick batch:

```graphql
mutation {
  # Create second product
  product2: createProduct(input: {
    sku: "LINDT-MILK-001"
    name: "Lindt Milk Chocolate Classic"
    slug: "lindt-milk-chocolate-classic"
    brandId: 1
    categoryId: 1
    description: "Smooth and creamy milk chocolate"
    weight: 100.0
    unitType: "GRAM"
    isActive: true
  }) {
    success
    message
    product { id name }
  }
  
  # Set price for product 2
  price2: setProductPrice(input: {
    productId: 2
    priceType: "RETAIL"
    basePrice: 35.00
    minQuantity: 1
  }) {
    success
    message
  }
  
  # Set inventory for product 2
  inventory2: updateInventory(input: {
    productId: 2
    quantityInStock: 300
  }) {
    success
    message
  }
}
```

---

## ✅ Step 9: Get All Products

```graphql
query {
  products {
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

---

## ✅ Step 10: Test Cart & Checkout (Customer Flow)

```graphql
mutation {
  addToCart(
    sessionId: "test-session-123"
    productId: 1
    quantity: 2
  ) {
    success
    message
    cart {
      id
      sessionId
      items {
        product {
          name
        }
        quantity
        totalPrice
      }
      totalItems
      totalPrice
    }
  }
}
```

---

## 🎯 Success Checklist

After completing all steps, you should have:

- ✅ 1 Category created
- ✅ 1 Brand created
- ✅ 2 Products created
- ✅ Prices set for both products
- ✅ Inventory updated
- ✅ Search working
- ✅ Cart working

---

## 🚨 Troubleshooting

### Error: "Brand or Category not found"
**Fix:** Make sure you use the correct IDs from steps 1 & 2

### Error: "Product not found"
**Fix:** Check the product was created successfully in step 3

### No results in search
**Fix:** Make sure `isActive: true` on your products

---

## 🎉 Next Tests

Try these mutations:

### Update a product
```graphql
mutation {
  updateProduct(id: 1, input: {
    name: "Lindt Excellence Dark 85% - UPDATED"
    featured: false
    brandId: 1
    categoryId: 1
  }) {
    success
    message
  }
}
```

### Deactivate a product
```graphql
mutation {
  deleteProduct(id: 2, hardDelete: false) {
    success
    message
  }
}
```

### Create an order
```graphql
mutation {
  createRetailOrder(input: {
    sessionId: "test-session-123"
    customerEmail: "test@example.com"
    customerPhone: "+971501234567"
    shippingAddress: {
      fullName: "Ahmed Al Maktoum"
      phoneNumber: "+971501234567"
      addressLine1: "Villa 123, Palm Jumeirah"
      city: "Dubai"
      emirate: "Dubai"
      postalCode: "12345"
    }
  }) {
    success
    message
    order {
      id
      orderNumber
      totalAmount
      status
    }
  }
}
```

---

**Ready? Copy Step 1 and paste it into GraphiQL!** 🚀

