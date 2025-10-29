# 🔧 Admin GraphQL API Guide

Complete guide for managing your e-commerce store through GraphQL mutations.

---

## 📋 Table of Contents

1. [Product Management](#product-management)
2. [Order Management](#order-management)
3. [Testing Examples](#testing-examples)
4. [Quick Start Workflow](#quick-start-workflow)

---

## 🛍️ Product Management

### 1. Create Category

```graphql
mutation {
  createCategory(input: {
    name: "Chocolates"
    slug: "chocolates"
    description: "Premium chocolate products"
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

**Response:**
```json
{
  "data": {
    "createCategory": {
      "success": true,
      "message": "Category 'Chocolates' created successfully",
      "category": {
        "id": "1",
        "name": "Chocolates",
        "slug": "chocolates"
      }
    }
  }
}
```

---

### 2. Update Category

```graphql
mutation {
  updateCategory(id: 1, input: {
    name: "Premium Chocolates"
    description: "Luxury chocolate collection"
  }) {
    success
    message
    category {
      id
      name
      description
    }
  }
}
```

---

### 3. Create Brand

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
    }
  }
}
```

---

### 4. Update Brand

```graphql
mutation {
  updateBrand(id: 1, input: {
    name: "Lindt Excellence"
    description: "Premium Swiss chocolate"
  }) {
    success
    message
    brand {
      id
      name
    }
  }
}
```

---

### 5. Create Product

```graphql
mutation {
  createProduct(input: {
    sku: "CHOC-001"
    name: "Dark Chocolate Bar 85%"
    slug: "dark-chocolate-bar-85"
    brandId: 1
    categoryId: 1
    description: "Rich dark chocolate with 85% cocoa"
    shortDescription: "Premium dark chocolate"
    ingredients: "Cocoa mass, cocoa butter, sugar"
    allergenInfo: "May contain traces of nuts"
    weight: 100.0
    unitType: "GRAM"
    isActive: true
    featured: true
  }) {
    success
    message
    product {
      id
      name
      sku
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

**Response:**
```json
{
  "data": {
    "createProduct": {
      "success": true,
      "message": "Product 'Dark Chocolate Bar 85%' created successfully",
      "product": {
        "id": "1",
        "name": "Dark Chocolate Bar 85%",
        "sku": "CHOC-001",
        "brand": {
          "name": "Lindt"
        },
        "category": {
          "name": "Chocolates"
        }
      }
    }
  }
}
```

---

### 6. Update Product

```graphql
mutation {
  updateProduct(id: 1, input: {
    name: "Dark Chocolate Bar 85% - Premium"
    description: "Updated description here"
    featured: false
    brandId: 1
    categoryId: 1
  }) {
    success
    message
    product {
      id
      name
      featured
    }
  }
}
```

---

### 7. Delete/Deactivate Product

```graphql
# Soft delete (deactivate)
mutation {
  deleteProduct(id: 1, hardDelete: false) {
    success
    message
  }
}

# Hard delete (permanent)
mutation {
  deleteProduct(id: 1, hardDelete: true) {
    success
    message
  }
}
```

---

### 8. Set Product Price

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
      basePrice
      salePrice
      priceType
    }
  }
}
```

**For Wholesale Pricing:**
```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "WHOLESALE"
    basePrice: 35.00
    minQuantity: 10
    isActive: true
  }) {
    success
    message
    price {
      id
      basePrice
      priceType
      minQuantity
    }
  }
}
```

---

### 9. Update Inventory

```graphql
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 500
    lowStockThreshold: 50
    warehouseLocation: "Warehouse A - Shelf 12"
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

---

## 📦 Order Management

### 1. Update Order Status

```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "Payment verified, preparing for shipping"
  }) {
    success
    message
    order {
      id
      orderNumber
      status
      statusHistory {
        status
        notes
        createdAt
      }
    }
  }
}
```

**Valid Statuses:**
- `PENDING` - Order received, awaiting payment
- `CONFIRMED` - Payment confirmed
- `PROCESSING` - Order being prepared
- `SHIPPED` - Order dispatched
- `DELIVERED` - Order delivered to customer
- `CANCELLED` - Order cancelled

---

### 2. Cancel Order

```graphql
mutation {
  cancelOrder(
    orderId: 1
    reason: "Customer requested cancellation"
  ) {
    success
    message
    order {
      id
      orderNumber
      status
    }
  }
}
```

**Note:** This automatically returns inventory to stock!

---

### 3. Update Shipping Address

```graphql
mutation {
  updateShippingAddress(
    orderId: 1
    fullName: "Ahmed Al Maktoum"
    phoneNumber: "+971501234567"
    addressLine1: "Villa 123, Palm Jumeirah"
    city: "Dubai"
    emirate: "Dubai"
    postalCode: "12345"
  ) {
    success
    message
    order {
      id
      shippingAddress {
        fullName
        phoneNumber
        city
        emirate
      }
    }
  }
}
```

---

## 🧪 Testing Examples

### Complete Product Setup Example

```graphql
# Step 1: Create Category
mutation CreateCategory {
  createCategory(input: {
    name: "Dark Chocolates"
    slug: "dark-chocolates"
    isActive: true
  }) {
    success
    message
    category { id name }
  }
}

# Step 2: Create Brand
mutation CreateBrand {
  createBrand(input: {
    name: "Lindt"
    slug: "lindt"
    countryOfOrigin: "Switzerland"
    isActive: true
  }) {
    success
    message
    brand { id name }
  }
}

# Step 3: Create Product (use IDs from above)
mutation CreateProduct {
  createProduct(input: {
    sku: "LINDT-DARK-001"
    name: "Lindt Excellence 85% Dark"
    slug: "lindt-excellence-85-dark"
    brandId: 1
    categoryId: 1
    description: "Intense dark chocolate with 85% cocoa"
    weight: 100.0
    unitType: "GRAM"
    isActive: true
    featured: true
  }) {
    success
    message
    product {
      id
      name
      sku
    }
  }
}

# Step 4: Set Retail Price
mutation SetRetailPrice {
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
    price { id basePrice salePrice }
  }
}

# Step 5: Update Inventory
mutation UpdateStock {
  updateInventory(input: {
    productId: 1
    quantityInStock: 1000
    lowStockThreshold: 100
  }) {
    success
    message
    inventory {
      quantityInStock
      isInStock
    }
  }
}
```

---

### Order Management Workflow

```graphql
# Step 1: View Order
query ViewOrder {
  order(id: 1) {
    id
    orderNumber
    status
    totalAmount
    items {
      product { name }
      quantity
      priceAtOrder
    }
  }
}

# Step 2: Confirm Order
mutation ConfirmOrder {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "Payment verified"
  }) {
    success
    message
  }
}

# Step 3: Process Order
mutation ProcessOrder {
  updateOrderStatus(input: {
    orderId: 1
    status: "PROCESSING"
    notes: "Picking items from warehouse"
  }) {
    success
    message
  }
}

# Step 4: Ship Order
mutation ShipOrder {
  updateOrderStatus(input: {
    orderId: 1
    status: "SHIPPED"
    notes: "Shipped via Aramex - Tracking: ABC123456"
  }) {
    success
    message
  }
}

# Step 5: Deliver Order
mutation DeliverOrder {
  updateOrderStatus(input: {
    orderId: 1
    status: "DELIVERED"
    notes: "Delivered to customer"
  }) {
    success
    message
  }
}
```

---

## 🚀 Quick Start Workflow

### Day 1: Initial Setup

```graphql
# 1. Create 3-5 categories
mutation { createCategory(input: {name: "Chocolates", slug: "chocolates"}) { success message } }
mutation { createCategory(input: {name: "Snacks", slug: "snacks"}) { success message } }
mutation { createCategory(input: {name: "Beverages", slug: "beverages"}) { success message } }

# 2. Create 5-10 brands
mutation { createBrand(input: {name: "Lindt", slug: "lindt", countryOfOrigin: "Switzerland"}) { success message } }
mutation { createBrand(input: {name: "Ferrero", slug: "ferrero", countryOfOrigin: "Italy"}) { success message } }
mutation { createBrand(input: {name: "Cadbury", slug: "cadbury", countryOfOrigin: "UK"}) { success message } }

# 3. Create your first product (see examples above)
```

### Day 2: Add More Products

Use the complete product setup example above to add 10-20 products.

### Day 3: Test Order Flow

1. Use frontend to add items to cart
2. Create order
3. Use admin mutations to manage orders

---

## 💡 Pro Tips

### 1. Batch Create Multiple Products

You can run multiple mutations in one request:

```graphql
mutation BatchCreate {
  product1: createProduct(input: {
    sku: "PROD-001"
    name: "Product 1"
    brandId: 1
    categoryId: 1
  }) {
    success
    product { id }
  }
  
  product2: createProduct(input: {
    sku: "PROD-002"
    name: "Product 2"
    brandId: 1
    categoryId: 1
  }) {
    success
    product { id }
  }
}
```

### 2. Always Check Success

```graphql
mutation {
  createProduct(input: {...}) {
    success      # ← Always check this!
    message      # ← Shows error details
    product { id }
  }
}
```

### 3. Use Variables

Instead of hardcoding values:

```graphql
mutation CreateProduct($input: ProductInput!) {
  createProduct(input: $input) {
    success
    message
    product { id name }
  }
}
```

**Variables:**
```json
{
  "input": {
    "sku": "PROD-001",
    "name": "My Product",
    "brandId": 1,
    "categoryId": 1
  }
}
```

---

## 🎯 Next Steps

1. **Test in GraphiQL**: `http://localhost:8000/graphql/`
2. **Create your first category**
3. **Create your first brand**
4. **Create your first product**
5. **Set price and inventory**
6. **Test on frontend!**

---

## 📞 Need Help?

Check the schema documentation in GraphiQL or run:

```graphql
query {
  __schema {
    mutationType {
      fields {
        name
        description
      }
    }
  }
}
```

This will show you all available mutations!

---

## 🔐 Security Note

**Important:** These are admin mutations! In production, you MUST:

1. Add authentication checks
2. Verify user is staff/admin
3. Add permission decorators
4. Use JWT tokens

Example with permission check:

```python
from graphql_jwt.decorators import staff_member_required

class CreateProduct(graphene.Mutation):
    @staff_member_required
    def mutate(self, info, input):
        # Your code here
```

---

**Ready to add your first products? Go to http://localhost:8000/graphql/ and try it out!** 🚀

