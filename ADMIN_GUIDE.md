# Admin API Guide - Complete Reference

This document lists all admin operations available in the GraphQL API. All admin mutations require **staff authentication** (JWT token with staff privileges).

---

## 🔐 Authentication

All admin operations require a valid JWT token from a staff user.

**Header Format:**
```
Authorization: Bearer <your-jwt-token>
```

**Important:** The header prefix must be `Bearer` (not `JWT`). The backend is configured to expect `Bearer` prefix.

**Get Token:**
```graphql
mutation {
  tokenAuth(username: "admin", password: "password") {
    token
    user {
      id
      username
      isStaff
    }
  }
}
```

---

## 📦 Products Management

### Categories

#### 1. Create Category
**Mutation:** `createCategory`

Create a new product category.

**Input Fields:**
- `name` (String, required) - Category name
- `slug` (String, optional) - URL-friendly slug (auto-generated if not provided)
- `description` (String, optional) - Category description
- `parent_category_id` (Int, optional) - Parent category for subcategories
- `is_active` (Boolean, optional, default: true) - Whether category is active
- `display_order` (Int, optional, default: 0) - Display order for sorting

**Example:**
```graphql
mutation {
  createCategory(input: {
    name: "Dark Chocolate"
    slug: "dark-chocolate"
    description: "Rich dark chocolate products"
    is_active: true
    display_order: 1
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

---

#### 2. Update Category
**Mutation:** `updateCategory`

Update an existing category.

**Arguments:**
- `id` (Int, required) - Category ID
- `input` (CategoryInput, required) - Category data

**Example:**
```graphql
mutation {
  updateCategory(id: 1, input: {
    name: "Premium Dark Chocolate"
    description: "Updated description"
    is_active: true
  }) {
    success
    message
    category {
      id
      name
    }
  }
}
```

---

### Brands

#### 3. Create Brand
**Mutation:** `createBrand`

Create a new brand.

**Input Fields:**
- `name` (String, required) - Brand name
- `slug` (String, optional) - URL-friendly slug
- `description` (String, optional) - Brand description
- `country_of_origin` (String, optional) - Country where brand originates
- `is_active` (Boolean, optional, default: true)
- `display_order` (Int, optional, default: 0)

**Example:**
```graphql
mutation {
  createBrand(input: {
    name: "Lindt"
    slug: "lindt"
    description: "Premium Swiss chocolate"
    country_of_origin: "Switzerland"
    is_active: true
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

#### 4. Update Brand
**Mutation:** `updateBrand`

Update an existing brand.

**Arguments:**
- `id` (Int, required) - Brand ID
- `input` (BrandInput, required) - Brand data

**Example:**
```graphql
mutation {
  updateBrand(id: 1, input: {
    name: "Lindt Excellence"
    description: "Updated description"
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

### Products

#### 5. Create Product
**Mutation:** `createProduct`

Create a new product. Automatically creates an inventory record with 0 stock.

**Input Fields:**
- `sku` (String, optional) - Product SKU (must be unique)
- `name` (String, required) - Product name
- `slug` (String, optional) - URL-friendly slug
- `brand_id` (Int, required) - Brand ID
- `category_id` (Int, required) - Category ID
- `description` (String, optional) - Full product description
- `short_description` (String, optional) - Short description
- `ingredients` (String, optional) - Ingredients list
- `allergen_info` (String, optional) - Allergen information
- `weight` (Decimal/String, optional) - Weight in grams
- `volume` (Decimal/String, optional) - Volume in ml
- `unit_type` (String, optional, default: "PIECE") - Unit type: "KG", "GRAM", "LITER", "BOTTLE", "PIECE", "BOX", "PACK"
- `is_active` (Boolean, optional, default: true)
- `featured` (Boolean, optional, default: false)

**Example:**
```graphql
mutation {
  createProduct(input: {
    sku: "LINDT-DARK-85"
    name: "Lindt Excellence Dark 85%"
    slug: "lindt-excellence-dark-85"
    brandId: 1
    categoryId: 1
    description: "Intense dark chocolate with 85% cocoa"
    shortDescription: "Premium dark chocolate bar"
    weight: "100.0"
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
```

---

#### 6. Update Product
**Mutation:** `updateProduct`

Update an existing product.

**Arguments:**
- `id` (Int, required) - Product ID
- `input` (ProductInput, required) - Product data

**Example:**
```graphql
mutation {
  updateProduct(id: 1, input: {
    name: "Updated Product Name"
    description: "Updated description"
    featured: false
    brandId: 1
    categoryId: 1
  }) {
    success
    message
    product {
      id
      name
    }
  }
}
```

---

#### 7. Delete Product
**Mutation:** `deleteProduct`

Delete or deactivate a product.

**Arguments:**
- `id` (Int, required) - Product ID
- `hard_delete` (Boolean, optional, default: false) - If true, permanently delete; if false, deactivate

**Example:**
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

### Pricing

#### 8. Set Product Price
**Mutation:** `setProductPrice`

Set or update product pricing.

**Input Fields:**
- `product_id` (Int, required) - Product ID
- `price_type` (String, required) - "RETAIL" or "WHOLESALE"
- `base_price` (Decimal/String, required) - Base price in AED
- `sale_price` (Decimal/String, optional) - Sale price (if on sale)
- `min_quantity` (Int, optional, default: 1) - Minimum quantity for this price tier
- `is_active` (Boolean, optional, default: true)

**Example:**
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
      basePrice
      salePrice
      effectivePrice
    }
  }
}
```

---

### Inventory

#### 9. Update Inventory
**Mutation:** `updateInventory`

Update product inventory/stock levels.

**Input Fields:**
- `product_id` (Int, required) - Product ID
- `quantity_in_stock` (Int, required) - Current stock quantity
- `low_stock_threshold` (Int, optional, default: 10) - Threshold for low stock warning
- `warehouse_location` (String, optional) - Warehouse location

**Example:**
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
      isInStock
      lowStockThreshold
    }
  }
}
```

---

### Product Images

#### 10. Upload Product Image
**Mutation:** `uploadProductImage`

Upload a product image. Images are automatically resized to max 1200x1200px.

**Input Fields:**
- `product_id` (Int, required) - Product ID
- `image` (String, required) - Base64 encoded image data (format: `data:image/jpeg;base64,<base64-string>`)
- `alt_text` (String, optional) - Alt text for image
- `is_primary` (Boolean, optional, default: false) - Mark as primary image
- `display_order` (Int, optional, default: 0) - Display order

**Example:**
```graphql
mutation {
  uploadProductImage(input: {
    productId: 1
    image: "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    altText: "Dark Chocolate Bar"
    isPrimary: true
    displayOrder: 1
  }) {
    success
    message
    productImage {
      id
      image
      altText
      isPrimary
    }
  }
}
```

---

#### 11. Delete Product Image
**Mutation:** `deleteProductImage`

Delete a product image.

**Arguments:**
- `image_id` (Int, required) - Image ID

**Example:**
```graphql
mutation {
  deleteProductImage(imageId: 1) {
    success
    message
  }
}
```

---

#### 12. Set Primary Image
**Mutation:** `setPrimaryImage`

Set a product image as the primary image (automatically un-sets other primary images).

**Arguments:**
- `image_id` (Int, required) - Image ID

**Example:**
```graphql
mutation {
  setPrimaryImage(imageId: 1) {
    success
    message
  }
}
```

---

### Product Variants

#### 13. Create Variant Options
**Mutation:** `createVariantOptions`

Create variant options for a product (e.g., Color: White/Dark, Weight: 500g/1000g).

**Arguments:**
- `product_id` (Int, required) - Product ID
- `options` (List of VariantOptionInput, required) - List of variant options

**VariantOptionInput Fields:**
- `name` (String, required) - Option name (e.g., "Color", "Weight")
- `values` (List of String, required) - List of option values (e.g., ["White", "Dark"])
- `display_order` (Int, optional) - Display order

**Example:**
```graphql
mutation {
  createVariantOptions(
    productId: 1
    options: [
      {
        name: "Color"
        values: ["White", "Dark", "Milk"]
        displayOrder: 1
      }
      {
        name: "Weight"
        values: ["500g", "1000g"]
        displayOrder: 2
      }
    ]
  ) {
    success
    message
    variantOptions {
      id
      name
      values {
        id
        value
      }
    }
  }
}
```

---

#### 14. Create Product Variant
**Mutation:** `createProductVariant`

Create a product variant (e.g., "Coco Mass White 500g").

**Input Fields:**
- `product_id` (Int, required) - Product ID
- `sku` (String, required) - Variant SKU (must be unique)
- `option_values` (JSON String, required) - JSON object with option names and values (e.g., `{"Color": "White", "Weight": "500g"}`)
- `price` (Decimal/String, required) - Variant price
- `sale_price` (Decimal/String, optional) - Sale price
- `currency` (String, optional, default: "AED")
- `quantity_in_stock` (Int, optional, default: 0) - Stock quantity
- `low_stock_threshold` (Int, optional, default: 10)
- `weight` (Decimal/String, optional) - Variant weight
- `is_active` (Boolean, optional, default: true)
- `is_default` (Boolean, optional, default: false) - Mark as default variant

**Example:**
```graphql
mutation {
  createProductVariant(input: {
    productId: 1
    sku: "PROD-001-WHITE-500"
    optionValues: "{\"Color\": \"White\", \"Weight\": \"500g\"}"
    price: "45.00"
    salePrice: "39.99"
    quantityInStock: 100
    isActive: true
    isDefault: true
  }) {
    success
    message
    variant {
      id
      sku
      price
    }
  }
}
```

---

#### 15. Update Product Variant
**Mutation:** `updateProductVariant`

Update an existing product variant.

**Arguments:**
- `variant_id` (Int, required) - Variant ID
- `price` (Decimal/String, optional)
- `sale_price` (Decimal/String, optional)
- `quantity_in_stock` (Int, optional)
- `low_stock_threshold` (Int, optional)
- `is_active` (Boolean, optional)
- `is_default` (Boolean, optional)

**Example:**
```graphql
mutation {
  updateProductVariant(
    variantId: 1
    price: "50.00"
    quantityInStock: 150
    isActive: true
  ) {
    success
    message
    variant {
      id
      sku
      price
    }
  }
}
```

---

#### 16. Delete Product Variant
**Mutation:** `deleteProductVariant`

Delete a product variant.

**Arguments:**
- `variant_id` (Int, required) - Variant ID

**Example:**
```graphql
mutation {
  deleteProductVariant(variantId: 1) {
    success
    message
  }
}
```

---

## 📦 Orders Management

### Order Status

#### 17. Update Order Status
**Mutation:** `updateOrderStatus`

Update the status of an order. Automatically creates a status history entry.

**Input Fields:**
- `order_id` (Int, required) - Order ID
- `status` (String, required) - New status: "PENDING", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"
- `notes` (String, optional) - Optional notes about the status change

**Example:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "SHIPPED"
    notes: "Order shipped via DHL, tracking: DHL123456"
  }) {
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

---

#### 18. Cancel Order
**Mutation:** `cancelOrder`

Cancel an order. Cannot cancel orders with status "DELIVERED" or "CANCELLED". Automatically returns inventory to stock.

**Arguments:**
- `order_id` (Int, required) - Order ID
- `reason` (String, optional) - Reason for cancellation

**Example:**
```graphql
mutation {
  cancelOrder(orderId: 1, reason: "Customer requested cancellation") {
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

---

#### 19. Update Shipping Address
**Mutation:** `updateShippingAddress`

Update the shipping address for an order.

**Arguments:**
- `order_id` (Int, required) - Order ID
- `full_name` (String, optional)
- `phone_number` (String, optional)
- `address_line1` (String, optional)
- `address_line2` (String, optional)
- `city` (String, optional)
- `emirate` (String, optional) - Must be uppercase: "DUBAI", "ABU_DHABI", etc.
- `postal_code` (String, optional)

**Example:**
```graphql
mutation {
  updateShippingAddress(
    orderId: 1
    fullName: "Jane Doe"
    phoneNumber: "+971509876543"
    addressLine1: "456 New Street"
    city: "Dubai"
    emirate: "DUBAI"
    postalCode: "12345"
  ) {
    success
    message
    order {
      id
      orderNumber
      shippingAddress {
        fullName
        city
        emirate
      }
    }
  }
}
```

---

## 🔍 Admin Queries

### Get Current User Info
**Query:** `me`

Get information about the currently authenticated admin user.

**Example:**
```graphql
query {
  me {
    id
    username
    email
    firstName
    lastName
    isStaff
    isSuperuser
  }
}
```

---

### Get All Orders
**Query:** `orders`

Get list of all orders (admin can see all orders).

**Arguments:**
- `status` (String, optional) - Filter by status
- `order_type` (String, optional) - Filter by order type
- `limit` (Int, optional) - Limit number of results

**Example:**
```graphql
query {
  orders(status: "PENDING", limit: 50) {
    id
    orderNumber
    status
    totalAmount
    customerName
    customerEmail
    createdAt
    items {
      productName
      quantity
      unitPrice
    }
  }
}
```

---

### Get Single Order
**Query:** `order`

Get details of a specific order by order number.

**Arguments:**
- `order_number` (String, required) - Order number

**Example:**
```graphql
query {
  order(orderNumber: "ORD-2024-001") {
    id
    orderNumber
    status
    totalAmount
    customerName
    customerEmail
    shippingAddress {
      fullName
      addressLine1
      city
      emirate
    }
    items {
      productName
      quantity
      unitPrice
      totalPrice
    }
    statusHistory {
      status
      createdAt
      notes
    }
  }
}
```

---

## 📝 Important Notes

### Data Types
- **Decimal values** (prices, weights) must be sent as **strings**: `"45.99"` not `45.99`
- **Unit types** must be exact strings: `"GRAM"`, `"KG"`, `"LITER"`, `"BOTTLE"`, `"PIECE"`, `"BOX"`, `"PACK"`

### Image Uploads
- Images must be base64 encoded
- Format: `data:image/jpeg;base64,<base64-string>`
- Images are automatically resized to max 1200x1200px
- JPEG format is recommended

### Error Handling
All mutations return:
- `success` (Boolean) - Whether the operation succeeded
- `message` (String) - Success or error message
- Always check `success` before using the returned data

### Authentication
- All admin mutations require a valid JWT token
- Token must be from a user with `is_staff=True`
- Token expires after 7 days
- Include token in header: `Authorization: JWT <token>`

---

## 🚀 Quick Start Workflow

1. **Authenticate** - Get JWT token
2. **Create Categories** - Set up product categories
3. **Create Brands** - Add brands
4. **Create Products** - Add products
5. **Set Prices** - Set product pricing
6. **Update Inventory** - Set stock quantities
7. **Upload Images** - Add product images
8. **Create Variants** (optional) - Add product variants if needed
9. **Manage Orders** - Update order statuses and shipping addresses

---

## 🔧 Troubleshooting

### "Not authorized" Error

If you're getting "Not authorized" errors, check the following:

1. **Header Format** (Most Common Issue):
   - ✅ Correct: `Authorization: Bearer <your-token>`
   - ❌ Wrong: `Authorization: JWT <your-token>`
   - The backend expects `Bearer` prefix, not `JWT`

2. **User Must Be Staff**:
   - The authenticated user must have `is_staff = True`
   - Check user permissions in Django admin or use the `me` query:
   ```graphql
   query {
     me {
       id
       username
       isStaff
       isSuperuser
     }
   }
   ```

3. **Token Expired**:
   - JWT tokens expire after 7 days
   - Get a new token using `tokenAuth` mutation

4. **Token Not Sent**:
   - Verify the token is included in the request headers
   - Check browser console/network tab to see if `Authorization` header is present

5. **CORS Issues**:
   - Ensure your frontend domain is in `CORS_ALLOWED_ORIGINS` in settings.py
   - For production, add your domain to the allowed origins list

### Verify Authentication

Test if your token is working:

```graphql
query {
  me {
    id
    username
    email
    isStaff
  }
}
```

If this returns `null`, your token is not being recognized. Check the header format.

---

## 📚 Related Documentation

- `FRONTEND_INTEGRATION.md` - Frontend developer guide
- `POSTMAN_COLLECTION.json` - Complete Postman collection with all mutations
- `ADMIN_API_GUIDE.md` - Detailed API documentation with examples

---

**Base API URL:** `http://164.90.215.173/graphql/`

