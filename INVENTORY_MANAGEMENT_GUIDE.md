# Inventory Management Guide - Complete Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Inventory Types](#inventory-types)
3. [Inventory Fields](#inventory-fields)
4. [Setting Inventory](#setting-inventory)
5. [Querying Inventory](#querying-inventory)
6. [Stock Availability](#stock-availability)
7. [Reserved Quantity](#reserved-quantity)
8. [Low Stock Alerts](#low-stock-alerts)
9. [Inventory and Orders](#inventory-and-orders)
10. [Best Practices](#best-practices)
11. [Common Scenarios](#common-scenarios)

---

## Overview

Your e-commerce platform has **two separate inventory systems**:

1. **Product Inventory** - For products without variants
2. **Variant Inventory** - For products with variants (each variant has its own stock)

Both systems support:
- ✅ Stock quantity tracking
- ✅ Reserved quantity (for pending orders)
- ✅ Available quantity (computed: in stock - reserved)
- ✅ Low stock threshold alerts
- ✅ Automatic stock reservation on order creation
- ✅ Automatic stock return on order cancellation

---

## Inventory Types

### 1. Product Inventory (Regular Products)

**Model:** `Inventory` (One-to-One with Product)

**When to use:**
- Products without variants
- Simple products with a single stock level

**Example:**
```
Product: "Lindt Excellence Dark 85%"
├─ Inventory
   ├─ quantity_in_stock: 500
   ├─ reserved_quantity: 15 (for pending orders)
   ├─ available_quantity: 485 (500 - 15)
   └─ is_in_stock: true
```

### 2. Variant Inventory (Products with Variants)

**Model:** `ProductVariant` (Each variant has its own inventory fields)

**When to use:**
- Products with variants (size, color, weight, etc.)
- Each variant needs separate stock tracking

**Example:**
```
Product: "Coco Mass"
├─ Variant: White 500g
│  ├─ quantity_in_stock: 150
│  ├─ reserved_quantity: 10
│  └─ available_quantity: 140
├─ Variant: White 1000g
│  ├─ quantity_in_stock: 100
│  ├─ reserved_quantity: 5
│  └─ available_quantity: 95
├─ Variant: Dark 500g
│  ├─ quantity_in_stock: 120
│  ├─ reserved_quantity: 0
│  └─ available_quantity: 120
└─ Variant: Dark 1000g
   ├─ quantity_in_stock: 80
   ├─ reserved_quantity: 8
   └─ available_quantity: 72
```

---

## Inventory Fields

### Product Inventory Fields

| Field | Type | Description |
|-------|------|-------------|
| `quantity_in_stock` | Integer | Total units in stock |
| `reserved_quantity` | Integer | Units reserved for pending orders |
| `available_quantity` | Integer (computed) | `quantity_in_stock - reserved_quantity` |
| `is_in_stock` | Boolean (computed) | `available_quantity > 0` |
| `is_low_stock` | Boolean (computed) | `available_quantity <= low_stock_threshold` |
| `low_stock_threshold` | Integer | Alert when stock falls below this |
| `warehouse_location` | String | Physical location in warehouse |
| `last_restocked_at` | DateTime | Last time stock was updated |

### Variant Inventory Fields

| Field | Type | Description |
|-------|------|-------------|
| `quantity_in_stock` | Integer | Total units in stock for this variant |
| `reserved_quantity` | Integer | Units reserved for pending orders |
| `available_quantity` | Integer (computed) | `quantity_in_stock - reserved_quantity` |
| `is_in_stock` | Boolean (computed) | `available_quantity > 0` |
| `is_low_stock` | Boolean (computed) | `available_quantity <= low_stock_threshold` |
| `low_stock_threshold` | Integer | Alert when stock falls below this |

**Note:** Variants don't have `warehouse_location` or `last_restocked_at` (use product-level fields if needed).

---

## Setting Inventory

### For Regular Products

**Admin Mutation:** `updateInventory`

**⚠️ Requires Authentication:** Admin staff token required (Bearer token)

**Input Fields:**
- `product_id` (Int, **required**) - Product ID
- `quantity_in_stock` (Int, **required**) - Total stock quantity
- `low_stock_threshold` (Int, optional, default: 10) - Low stock alert threshold
- `warehouse_location` (String, optional) - Warehouse location

**Example 1: Set Initial Stock**

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
      availableQuantity
      isInStock
      lowStockThreshold
      warehouseLocation
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "updateInventory": {
      "success": true,
      "message": "Inventory updated for 'Lindt Excellence Dark 85%': 500 units",
      "inventory": {
        "id": "1",
        "quantityInStock": 500,
        "availableQuantity": 500,
        "isInStock": true,
        "lowStockThreshold": 50,
        "warehouseLocation": "Warehouse A - Shelf 12"
      }
    }
  }
}
```

**Example 2: Update Stock After Restock**

```graphql
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 750  # Updated from 500
    lowStockThreshold: 50
  }) {
    success
    inventory {
      quantityInStock
      availableQuantity
    }
  }
}
```

### For Variants

**Admin Mutation:** `createProductVariant` or `updateProductVariant`

**When Creating Variant:**

```graphql
mutation {
  createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-500"
    optionValues: "{\"Color\": \"White\", \"Weight\": \"500g\"}"
    price: "25.00"
    quantityInStock: 150  # Set initial stock
    lowStockThreshold: 15
  }) {
    success
    variant {
      id
      sku
      quantityInStock
      availableQuantity
      isInStock
    }
  }
}
```

**When Updating Variant Stock:**

```graphql
mutation {
  updateProductVariant(
    variantId: 1
    quantityInStock: 200  # Update stock
    lowStockThreshold: 20
  ) {
    success
    message
    variant {
      sku
      quantityInStock
      availableQuantity
      isInStock
    }
  }
}
```

**Example: Bulk Update Multiple Variants**

```graphql
mutation {
  # Variant 1
  v1: updateProductVariant(
    variantId: 1
    quantityInStock: 150
  ) {
    success
    variant { sku quantityInStock }
  }
  
  # Variant 2
  v2: updateProductVariant(
    variantId: 2
    quantityInStock: 100
  ) {
    success
    variant { sku quantityInStock }
  }
  
  # Variant 3
  v3: updateProductVariant(
    variantId: 3
    quantityInStock: 120
  ) {
    success
    variant { sku quantityInStock }
  }
}
```

---

## Querying Inventory

### For Regular Products

#### Get Product with Inventory

```graphql
query {
  product(id: 1) {
    id
    name
    inventory {
      id
      quantityInStock
      reservedQuantity
      availableQuantity
      isInStock
      isLowStock
      lowStockThreshold
      warehouseLocation
      lastRestockedAt
    }
    inStock  # Quick computed field (boolean)
  }
}
```

**Response:**
```json
{
  "data": {
    "product": {
      "id": "1",
      "name": "Lindt Excellence Dark 85%",
      "inventory": {
        "id": "1",
        "quantityInStock": 500,
        "reservedQuantity": 15,
        "availableQuantity": 485,
        "isInStock": true,
        "isLowStock": false,
        "lowStockThreshold": 50,
        "warehouseLocation": "Warehouse A - Shelf 12",
        "lastRestockedAt": "2024-01-15T10:30:00Z"
      },
      "inStock": true
    }
  }
}
```

#### Get Multiple Products with Inventory

```graphql
query {
  products(limit: 10) {
    id
    name
    inStock  # Quick boolean check
    inventory {
      availableQuantity
      isLowStock
    }
  }
}
```

#### Filter Products by Stock Status

```graphql
query {
  products(
    inStock: true  # Only show products in stock
    limit: 20
  ) {
    id
    name
    inventory {
      availableQuantity
    }
  }
}
```

### For Variant Products

#### Get Product with Variants and Their Inventory

```graphql
query {
  product(id: 5) {
    id
    name
    variants {
      id
      sku
      quantityInStock
      reservedQuantity
      availableQuantity
      isInStock
      isLowStock
      lowStockThreshold
      optionValues {
        value
        option {
          name
        }
      }
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "product": {
      "id": "5",
      "name": "Coco Mass",
      "variants": [
        {
          "id": "1",
          "sku": "COCO-WHITE-500",
          "quantityInStock": 150,
          "reservedQuantity": 10,
          "availableQuantity": 140,
          "isInStock": true,
          "isLowStock": false,
          "lowStockThreshold": 15,
          "optionValues": [
            {"value": "White", "option": {"name": "Color"}},
            {"value": "500g", "option": {"name": "Weight"}}
          ]
        },
        {
          "id": "2",
          "sku": "COCO-WHITE-1000",
          "quantityInStock": 100,
          "reservedQuantity": 5,
          "availableQuantity": 95,
          "isInStock": true,
          "isLowStock": false,
          "lowStockThreshold": 15,
          "optionValues": [
            {"value": "White", "option": {"name": "Color"}},
            {"value": "1000g", "option": {"name": "Weight"}}
          ]
        }
      ]
    }
  }
}
```

---

## Stock Availability

### Understanding Available Quantity

**Available Quantity** = `quantity_in_stock - reserved_quantity`

This is the actual quantity available for new orders.

**Example:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 500 (total in warehouse)
├─ reserved_quantity: 15 (in pending orders)
└─ available_quantity: 485 (can sell 485 more units)
```

### Checking Stock Before Adding to Cart

**Frontend should check stock before allowing add to cart:**

```javascript
// For regular products
const product = {
  inventory: {
    availableQuantity: 485,
    isInStock: true
  }
}

if (!product.inventory.isInStock) {
  showError("Product is out of stock")
} else if (product.inventory.availableQuantity < requestedQuantity) {
  showError(`Only ${product.inventory.availableQuantity} available`)
} else {
  addToCart(product, requestedQuantity)
}

// For variants
const variant = {
  availableQuantity: 140,
  isInStock: true
}

if (!variant.isInStock || variant.availableQuantity < requestedQuantity) {
  showError("Not enough stock")
} else {
  addToCart(variant, requestedQuantity)
}
```

### Stock Validation During Checkout

**The backend automatically validates stock when creating an order:**

- ✅ Checks if product/variant is in stock
- ✅ Checks if available quantity >= requested quantity
- ✅ Returns clear error messages if stock is insufficient

**Example Error Responses:**
```json
{
  "data": {
    "createRetailOrder": {
      "success": false,
      "message": "Not enough stock for Coco Mass - White, 500g. Only 140 available"
    }
  }
}
```

---

## Reserved Quantity

### How Reserved Quantity Works

When an order is created, inventory is **automatically reserved**:

1. Customer adds items to cart → **No reservation yet**
2. Customer creates order → **Inventory reserved** (moved from `quantity_in_stock` to `reserved_quantity`)
3. Order status changes:
   - **DELIVERED** → Reserved quantity stays (order completed)
   - **CANCELLED** → Reserved quantity returned to stock

### Reserved Quantity Calculation

```
For Regular Products:
reserved_quantity = Sum of all quantities in pending orders

For Variants:
variant.reserved_quantity = Sum of all quantities for this variant in pending orders
```

### Example: Reservation Flow

**Initial State:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 500
├─ reserved_quantity: 0
└─ available_quantity: 500
```

**Customer creates order (5 units):**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 500 (unchanged)
├─ reserved_quantity: 5 (increased)
└─ available_quantity: 495 (decreased)
```

**Order is DELIVERED:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 495 (decreased by 5)
├─ reserved_quantity: 0 (returned)
└─ available_quantity: 495
```

**Order is CANCELLED:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 500 (returned)
├─ reserved_quantity: 0 (cleared)
└─ available_quantity: 500 (restored)
```

### Manual Reserved Quantity Management

**⚠️ Warning:** Reserved quantity is automatically managed by the system. You should NOT manually update `reserved_quantity` unless you know what you're doing.

**Current behavior:**
- Reserved quantity increases when order is created
- Reserved quantity decreases when order is delivered/cancelled
- Reserved quantity is automatically calculated based on pending orders

---

## Low Stock Alerts

### Understanding Low Stock

**Low Stock** = `available_quantity <= low_stock_threshold`

This indicates when you should restock.

### Setting Low Stock Threshold

**For Regular Products:**

```graphql
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 500
    lowStockThreshold: 50  # Alert when <= 50 units available
  }) {
    success
    inventory {
      isLowStock
      lowStockThreshold
    }
  }
}
```

**For Variants:**

```graphql
mutation {
  updateProductVariant(
    variantId: 1
    quantityInStock: 150
    lowStockThreshold: 15  # Alert when <= 15 units available
  ) {
    success
    variant {
      isLowStock
      lowStockThreshold
    }
  }
}
```

### Querying Low Stock Products

**For Regular Products:**

```graphql
query {
  products {
    id
    name
    inventory {
      availableQuantity
      isLowStock
      lowStockThreshold
    }
  }
}
```

**Then filter in frontend:**
```javascript
const lowStockProducts = products.filter(
  p => p.inventory?.isLowStock === true
)
```

**For Variants:**

```graphql
query {
  product(id: 5) {
    name
    variants {
      sku
      availableQuantity
      isLowStock
      lowStockThreshold
    }
  }
}
```

### Recommended Thresholds

- **Fast-moving products:** 10-20% of average monthly sales
- **Slow-moving products:** 5-10 units
- **Seasonal products:** Higher threshold before season
- **Bulk/wholesale items:** 50-100 units

---

## Inventory and Orders

### Order Creation → Inventory Reservation

**Automatic Process:**

1. Customer adds items to cart → **No reservation**
2. Customer creates order → **Stock validated**:
   - Checks if `available_quantity >= order_quantity`
   - Returns error if insufficient stock
3. If stock is sufficient → **Order created and inventory reserved**:
   - `reserved_quantity += order_quantity`
   - `available_quantity` decreases

**Example:**

```graphql
# Customer creates order with 5 units
mutation {
  createRetailOrder(
    sessionKey: "cart-123"
    customerInfo: { ... }
    shippingAddress: { ... }
  ) {
    success
    message
    order {
      id
      orderNumber
      items {
        productName
        quantity
      }
    }
  }
}
```

**Before Order:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 500
├─ reserved_quantity: 0
└─ available_quantity: 500
```

**After Order Created:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 500
├─ reserved_quantity: 5  ← Reserved for this order
└─ available_quantity: 495
```

### Order Cancellation → Inventory Return

**Automatic Process:**

When an order is cancelled (by admin), inventory is automatically returned:

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
      status
    }
  }
}
```

**Inventory automatically updated:**
```
Product: Lindt Chocolate
├─ quantity_in_stock: 505  ← Returned (500 + 5)
├─ reserved_quantity: 0    ← Cleared
└─ available_quantity: 505
```

**⚠️ Important:**
- Cancelled orders automatically return inventory to stock
- Orders with status `DELIVERED` or `CANCELLED` cannot be cancelled again
- Only admins can cancel orders

### Order Delivery → Inventory Deduction

When an order is marked as `DELIVERED`, the reserved quantity should be deducted from total stock (this happens when order status changes).

**Manual Update Required (if not automated):**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "DELIVERED"
  }) {
    success
    order {
      status
    }
  }
}
```

**Note:** The system may need manual inventory adjustment for delivered orders, depending on your workflow.

---

## Best Practices

### 1. **Always Set Inventory After Creating Products**

```graphql
# Step 1: Create product
mutation {
  createProduct(input: { ... }) {
    success
    product { id }
  }
}

# Step 2: Set inventory immediately
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 500
    lowStockThreshold: 50
  }) {
    success
  }
}
```

### 2. **Set Realistic Low Stock Thresholds**

- Fast-moving: 10-20% of monthly sales
- Slow-moving: 5-10 units
- Seasonal: Adjust before season

### 3. **Regular Stock Updates**

Update inventory:
- After receiving new shipments
- After physical stock counts
- After major sales events

### 4. **Monitor Reserved Quantity**

Check reserved quantities regularly:
- Long-pending orders may need attention
- Reserved quantities should match pending orders

### 5. **Variant Stock Management**

For variant products:
- Each variant has independent stock
- Track stock per variant, not per product
- Set thresholds per variant

### 6. **Warehouse Location**

Use `warehouse_location` for:
- Physical organization
- Restocking efficiency
- Multi-warehouse tracking (if expanded)

---

## Common Scenarios

### Scenario 1: Initial Product Setup

**Goal:** Create product and set initial stock

```graphql
# 1. Create product
mutation {
  createProduct(input: {
    name: "Lindt Excellence Dark 85%"
    brandId: 1
    categoryId: 1
    sku: "LINDT-DARK-85"
    unitType: "GRAM"
    weight: "100.0"
  }) {
    success
    product { id name }
  }
}

# 2. Set inventory
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 500
    lowStockThreshold: 50
    warehouseLocation: "Warehouse A - Shelf 12"
  }) {
    success
    inventory {
      quantityInStock
      availableQuantity
      isInStock
    }
  }
}
```

### Scenario 2: Restocking Products

**Goal:** Update stock after receiving new inventory

```graphql
mutation {
  updateInventory(input: {
    productId: 1
    quantityInStock: 750  # Add 250 units
    lowStockThreshold: 50
  }) {
    success
    inventory {
      quantityInStock
      availableQuantity
    }
  }
}
```

### Scenario 3: Setting Variant Stock

**Goal:** Create variants with different stock levels

```graphql
mutation {
  # Variant 1: White 500g
  v1: createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-500"
    optionValues: "{\"Weight\": \"500g\"}"
    price: "25.00"
    quantityInStock: 150
    lowStockThreshold: 15
  }) {
    success
    variant { sku quantityInStock }
  }
  
  # Variant 2: White 1000g
  v2: createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-1000"
    optionValues: "{\"Weight\": \"1000g\"}"
    price: "45.00"
    quantityInStock: 100
    lowStockThreshold: 10
  }) {
    success
    variant { sku quantityInStock }
  }
}
```

### Scenario 4: Check Stock Before Display

**Goal:** Only show in-stock products on homepage

```graphql
query {
  products(
    inStock: true  # Filter by stock
    featured: true
    limit: 8
  ) {
    id
    name
    retailPrice
    inStock
    inventory {
      availableQuantity
    }
    images {
      image
      isPrimary
    }
  }
}
```

### Scenario 5: Low Stock Alert Query

**Goal:** Get all products/variants with low stock

```graphql
# For regular products
query {
  products(limit: 100) {
    id
    name
    inventory {
      availableQuantity
      isLowStock
      lowStockThreshold
    }
  }
}

# For variants
query {
  products(limit: 50) {
    id
    name
    variants {
      sku
      availableQuantity
      isLowStock
      lowStockThreshold
    }
  }
}
```

**Frontend filtering:**
```javascript
// Filter low stock items
const lowStockItems = products
  .filter(p => p.inventory?.isLowStock)
  .concat(
    products
      .filter(p => p.variants)
      .flatMap(p => 
        p.variants
          .filter(v => v.isLowStock)
          .map(v => ({ product: p.name, variant: v.sku, ...v }))
      )
  )
```

### Scenario 6: Bulk Stock Update

**Goal:** Update multiple products after inventory count

```graphql
mutation {
  # Product 1
  p1: updateInventory(input: {
    productId: 1
    quantityInStock: 485
  }) {
    success
    inventory { quantityInStock }
  }
  
  # Product 2
  p2: updateInventory(input: {
    productId: 2
    quantityInStock: 320
  }) {
    success
    inventory { quantityInStock }
  }
  
  # Product 3
  p3: updateInventory(input: {
    productId: 3
    quantityInStock: 250
  }) {
    success
    inventory { quantityInStock }
  }
}
```

### Scenario 7: Stock Check for Frontend

**Goal:** Check stock before allowing add to cart

```graphql
# For regular product
query {
  product(id: 1) {
    id
    name
    inStock
    inventory {
      availableQuantity
      isLowStock
    }
  }
}

# For variant product
query {
  product(id: 5) {
    id
    name
    variants {
      id
      sku
      isInStock
      availableQuantity
      isLowStock
    }
  }
}
```

**Frontend logic:**
```javascript
// Regular product
if (!product.inStock) {
  disableAddToCart("Out of stock")
} else if (product.inventory.availableQuantity < quantity) {
  disableAddToCart(`Only ${product.inventory.availableQuantity} available`)
} else {
  enableAddToCart()
}

// Variant product
const selectedVariant = product.variants.find(v => v.id === variantId)
if (!selectedVariant.isInStock) {
  disableAddToCart("Variant out of stock")
} else if (selectedVariant.availableQuantity < quantity) {
  disableAddToCart(`Only ${selectedVariant.availableQuantity} available`)
} else {
  enableAddToCart()
}
```

---

## Summary

### ✅ **Key Takeaways**

1. **Two inventory systems:**
   - Regular products → `updateInventory` mutation
   - Variants → Set `quantityInStock` when creating/updating variant

2. **Inventory fields:**
   - `quantity_in_stock` - Total in warehouse
   - `reserved_quantity` - Reserved for pending orders
   - `available_quantity` - Available for new orders (computed)
   - `is_in_stock` - Boolean check (computed)
   - `is_low_stock` - Low stock alert (computed)

3. **Automatic processes:**
   - Stock validation on order creation
   - Inventory reservation on order creation
   - Inventory return on order cancellation

4. **Querying:**
   - Use `inStock` for quick boolean check
   - Use `inventory` object for detailed info
   - Filter with `inStock: true` parameter

5. **Best practices:**
   - Set inventory after creating products
   - Set realistic low stock thresholds
   - Regular stock updates
   - Monitor reserved quantities

---

## Quick Reference

### Admin Mutations

| Mutation | Purpose | Auth Required |
|----------|---------|---------------|
| `updateInventory` | Set/update product inventory | ✅ Yes |
| `createProductVariant` | Create variant with stock | ✅ Yes |
| `updateProductVariant` | Update variant stock | ✅ Yes |

### Public Queries

| Query | Field | Description |
|-------|-------|-------------|
| `product(id)` | `inStock` | Quick boolean check |
| `product(id)` | `inventory` | Full inventory details |
| `product(id)` | `variants[].isInStock` | Variant stock status |
| `products()` | `inStock` parameter | Filter by stock status |

### Computed Fields

| Field | Type | Calculation |
|-------|------|-------------|
| `availableQuantity` | Integer | `quantity_in_stock - reserved_quantity` |
| `isInStock` | Boolean | `available_quantity > 0` |
| `isLowStock` | Boolean | `available_quantity <= low_stock_threshold` |

---

**🎉 You're ready to manage inventory in your e-commerce platform!**

For product management, see: `ADMIN_GUIDE.md`  
For pricing, see: `PRICING_CATALOG_GUIDE.md`  
For variants, see: `PRODUCT_VARIANTS_GUIDE.md`

