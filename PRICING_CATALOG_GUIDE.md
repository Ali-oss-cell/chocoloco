# Pricing Catalog Guide - Complete Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Pricing Structure](#pricing-structure)
3. [Setting Prices for Regular Products](#setting-prices-for-regular-products)
4. [Setting Prices for Variants](#setting-prices-for-variants)
5. [Querying Prices](#querying-prices)
6. [Filtering Products by Price](#filtering-products-by-price)
7. [Updating Prices](#updating-prices)
8. [Sale Prices & Discounts](#sale-prices--discounts)
9. [Price Display Logic](#price-display-logic)
10. [Best Practices](#best-practices)
11. [Common Scenarios](#common-scenarios)

---

## Overview

Your e-commerce platform supports **two types of pricing**:

1. **Regular Product Pricing** - For products without variants
2. **Variant Pricing** - For products with variants (each variant has its own price)

### Key Concepts

- **Base Price**: The regular/standard price
- **Sale Price**: Optional discounted price
- **Effective Price**: Automatically calculated (sale price if available, otherwise base price)
- **Currency**: AED (default) - all prices are in AED
- **Price Type**: Currently only `RETAIL` is supported (wholesale pricing is planned for future)

---

## Pricing Structure

### Regular Products (No Variants)

Products without variants use the `ProductPrice` model:
- One product can have multiple price tiers (quantity-based pricing)
- Each price tier has: `base_price`, optional `sale_price`, `min_quantity`
- Example: Product "Lindt Chocolate Bar" - Single price: 49.99 AED

### Variant Products

Products with variants use the `ProductVariant` model:
- Each variant has its own independent pricing
- Variants can have different prices based on size, color, etc.
- Example: Product "Coco Mass" with variants:
  - White 500g: 25.00 AED
  - White 1000g: 45.00 AED
  - Dark 500g: 28.00 AED
  - Dark 1000g: 50.00 AED

---

## Setting Prices for Regular Products

### Admin Mutation: `setProductPrice`

**⚠️ Requires Authentication:** Admin staff token required (Bearer token)

**Purpose:** Set or update the retail price for a product without variants.

**Input Fields:**
- `product_id` (Int, **required**) - Product ID
- `price_type` (String, **required**) - Currently only `"RETAIL"` is supported
- `base_price` (Decimal/String, **required**) - Regular price (e.g., `"49.99"`)
- `sale_price` (Decimal/String, optional) - Discounted price (e.g., `"39.99"`)
- `min_quantity` (Int, optional, default: 1) - Minimum quantity for this price tier
- `is_active` (Boolean, optional, default: true) - Enable/disable this price

### Example 1: Set Basic Price

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
  }) {
    success
    message
    price {
      id
      basePrice
      salePrice
      effectivePrice
      currency
      isActive
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "setProductPrice": {
      "success": true,
      "message": "Price created for 'Lindt Excellence Dark 85%'",
      "price": {
        "id": "1",
        "basePrice": "49.99",
        "salePrice": null,
        "effectivePrice": "49.99",
        "currency": "AED",
        "isActive": true
      }
    }
  }
}
```

### Example 2: Set Price with Sale

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
    salePrice: "39.99"
  }) {
    success
    message
    price {
      basePrice
      salePrice
      effectivePrice
    }
  }
}
```

**Response:**
```json
{
  "setProductPrice": {
    "success": true,
    "price": {
      "basePrice": "49.99",
      "salePrice": "39.99",
      "effectivePrice": "39.99"  // Automatically uses sale price
    }
  }
}
```

### Example 3: Quantity-Based Pricing

```graphql
# Price for single item (1-4 items)
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
    minQuantity: 1
  }) {
    success
    price { id basePrice minQuantity }
  }
}

# Bulk price (5+ items) - requires creating another price entry
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "44.99"
    minQuantity: 5
  }) {
    success
    price { id basePrice minQuantity }
  }
}
```

**Note:** The system currently supports quantity tiers, but frontend should select the appropriate price tier based on cart quantity.

---

## Setting Prices for Variants

### Admin Mutation: `createProductVariant`

When creating a variant, set its price directly:

**Input Fields:**
- `product_id` (Int, **required**)
- `sku` (String, **required**)
- `option_values` (JSON String, **required**)
- `price` (Decimal/String, **required**) - Variant base price
- `sale_price` (Decimal/String, optional) - Variant sale price
- `currency` (String, optional, default: "AED")
- ... other fields

### Example: Create Variant with Price

```graphql
mutation {
  createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-500"
    optionValues: "{\"Color\": \"White\", \"Weight\": \"500g\"}"
    price: "25.00"
    salePrice: null
    currency: "AED"
    quantityInStock: 150
    weight: "500"
  }) {
    success
    message
    variant {
      id
      sku
      price
      salePrice
      effectivePrice
    }
  }
}
```

### Example: Multiple Variants with Different Prices

```graphql
# Variant 1: White 500g - Standard price
mutation {
  v1: createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-500"
    optionValues: "{\"Color\": \"White\", \"Weight\": \"500g\"}"
    price: "25.00"
    quantityInStock: 150
  }) {
    success
    variant { sku price }
  }
}

# Variant 2: White 1000g - Bulk discount
mutation {
  v2: createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-1000"
    optionValues: "{\"Color\": \"White\", \"Weight\": \"1000g\"}"
    price: "45.00"
    quantityInStock: 100
  }) {
    success
    variant { sku price }
  }
}

# Variant 3: Dark 500g - Premium price
mutation {
  v3: createProductVariant(input: {
    productId: 5
    sku: "COCO-DARK-500"
    optionValues: "{\"Color\": \"Dark\", \"Weight\": \"500g\"}"
    price: "28.00"
    quantityInStock: 120
  }) {
    success
    variant { sku price }
  }
}

# Variant 4: Dark 1000g - Bulk discount
mutation {
  v4: createProductVariant(input: {
    productId: 5
    sku: "COCO-DARK-1000"
    optionValues: "{\"Color\": \"Dark\", \"Weight\": \"1000g\"}"
    price: "50.00"
    quantityInStock: 80
  }) {
    success
    variant { sku price }
  }
}
```

---

## Querying Prices

### For Regular Products

#### Get Product with Price

```graphql
query {
  product(id: 1) {
    id
    name
    retailPrice  # Computed field - effective price (sale if available, else base)
    prices {
      id
      priceType
      basePrice
      salePrice
      effectivePrice  # Computed: salePrice if available, else basePrice
      currency
      minQuantity
      isActive
    }
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
      "retailPrice": "39.99",
      "prices": [
        {
          "id": "1",
          "priceType": "RETAIL",
          "basePrice": "49.99",
          "salePrice": "39.99",
          "effectivePrice": "39.99",
          "currency": "AED",
          "minQuantity": 1,
          "isActive": true
        }
      ]
    }
  }
}
```

#### Get Multiple Products with Prices

```graphql
query {
  products(limit: 10) {
    id
    name
    retailPrice  # Quick access to effective price
    prices {
      basePrice
      salePrice
      effectivePrice
    }
  }
}
```

### For Variant Products

#### Get Product with Variants and Their Prices

```graphql
query {
  product(id: 5) {
    id
    name
    variants {
      id
      sku
      price          # Base price
      salePrice      # Optional sale price
      effectivePrice # Computed: salePrice if available, else price
      currency
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
          "price": "25.00",
          "salePrice": null,
          "effectivePrice": "25.00",
          "currency": "AED",
          "optionValues": [
            {"value": "White", "option": {"name": "Color"}},
            {"value": "500g", "option": {"name": "Weight"}}
          ]
        },
        {
          "id": "2",
          "sku": "COCO-WHITE-1000",
          "price": "45.00",
          "salePrice": null,
          "effectivePrice": "45.00",
          "currency": "AED",
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

## Filtering Products by Price

You can filter products by price range in the `products` query:

### Filter by Price Range

```graphql
query {
  products(
    minPrice: "20.00"
    maxPrice: "50.00"
    limit: 20
  ) {
    id
    name
    retailPrice
    prices {
      basePrice
      effectivePrice
    }
  }
}
```

**Note:** Price filters work on `basePrice` (not sale price) and only apply to products with `price_type='RETAIL'` and `is_active=true`.

### Sort by Price

```graphql
query {
  products(
    sortBy: "price_asc"  # or "price_desc"
    limit: 20
  ) {
    id
    name
    retailPrice
  }
}
```

**Available sort options:**
- `price_asc` - Lowest price first
- `price_desc` - Highest price first
- `name` - Alphabetical
- `newest` - Most recently created
- `oldest` - Oldest first

### Combined Filters

```graphql
query {
  products(
    category: "dark-chocolate"
    minPrice: "30.00"
    maxPrice: "100.00"
    featured: true
    sortBy: "price_asc"
    limit: 10
  ) {
    id
    name
    retailPrice
    brand {
      name
    }
  }
}
```

---

## Updating Prices

### Update Regular Product Price

Use the same `setProductPrice` mutation - it will update if a price already exists:

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "54.99"  # Updated from 49.99
    salePrice: "44.99"  # Updated from 39.99
  }) {
    success
    message
    price {
      basePrice
      salePrice
      effectivePrice
    }
  }
}
```

### Update Variant Price

**Mutation:** `updateProductVariant`

```graphql
mutation {
  updateProductVariant(
    variantId: 1
    price: "27.50"        # Update base price
    salePrice: "24.99"    # Add/update sale price
  ) {
    success
    message
    variant {
      sku
      price
      salePrice
      effectivePrice
    }
  }
}
```

### Remove Sale Price

Set `salePrice` to `null`:

```graphql
mutation {
  updateProductVariant(
    variantId: 1
    salePrice: null       # Remove sale price
  ) {
    success
    variant {
      price
      salePrice          # Will be null
      effectivePrice     # Will equal base price
    }
  }
}
```

### Deactivate a Price

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
    isActive: false      # Deactivate this price
  }) {
    success
    price {
      isActive
    }
  }
}
```

**Note:** Deactivated prices won't appear in `prices` queries (only active prices are returned).

---

## Sale Prices & Discounts

### How Sale Prices Work

1. **If `salePrice` is set:** `effectivePrice = salePrice`
2. **If `salePrice` is null:** `effectivePrice = basePrice`
3. **Sale price must be less than base price** (enforced by business logic, not database)

### Example: Seasonal Sale

```graphql
# Put product on sale
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
    salePrice: "39.99"  # 20% off
  }) {
    success
    price {
      basePrice
      salePrice
      effectivePrice  # 39.99
    }
  }
}
```

### Example: Selective Variant Sale

```graphql
# Put only the 1000g variants on sale
mutation {
  # White 1000g on sale
  v1: updateProductVariant(
    variantId: 2
    salePrice: "39.99"  # Was 45.00
  ) {
    success
    variant { sku salePrice effectivePrice }
  }
  
  # Dark 1000g on sale
  v2: updateProductVariant(
    variantId: 4
    salePrice: "44.99"  # Was 50.00
  ) {
    success
    variant { sku salePrice effectivePrice }
  }
}
```

### End a Sale

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
    salePrice: null  # Remove sale
  }) {
    success
    price {
      effectivePrice  # Now equals basePrice
    }
  }
}
```

---

## Price Display Logic

### For Frontend Developers

#### Regular Products (No Variants)

```javascript
// Query
const product = {
  retailPrice: "39.99",  // Use this for display (already calculated)
  prices: [{
    basePrice: "49.99",
    salePrice: "39.99",
    effectivePrice: "39.99"
  }]
}

// Display logic
if (product.prices[0].salePrice) {
  // Show: ~~49.99 AED~~ 39.99 AED (Sale!)
  showPrice(product.prices[0].salePrice, product.prices[0].basePrice, true)
} else {
  // Show: 49.99 AED
  showPrice(product.prices[0].basePrice)
}

// OR simply use:
showPrice(product.retailPrice)  // Already the effective price
```

#### Variant Products

```javascript
// Query
const product = {
  variants: [
    {
      price: "25.00",
      salePrice: null,
      effectivePrice: "25.00",
      optionValues: [...]
    },
    {
      price: "45.00",
      salePrice: "39.99",
      effectivePrice: "39.99",
      optionValues: [...]
    }
  ]
}

// Display logic for selected variant
const selectedVariant = product.variants.find(v => v.id === selectedId)

if (selectedVariant.salePrice) {
  // Show: ~~45.00 AED~~ 39.99 AED
  showPrice(selectedVariant.salePrice, selectedVariant.price, true)
} else {
  // Show: 25.00 AED
  showPrice(selectedVariant.price)
}

// OR simply use:
showPrice(selectedVariant.effectivePrice)  // Already calculated
```

### Recommended Display Format

```
Regular: 49.99 AED
On Sale: ~~49.99 AED~~ 39.99 AED (Save 20%)
```

---

## Best Practices

### 1. **Always Set Prices After Creating Products**

```graphql
# Step 1: Create product
mutation {
  createProduct(input: { ... }) {
    success
    product { id name }
  }
}

# Step 2: Set price immediately
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
  }) {
    success
  }
}
```

### 2. **Use String Format for Prices**

In GraphQL mutations, use strings for decimal values:

```graphql
# ✅ Correct
basePrice: "49.99"
salePrice: "39.99"

# ❌ Incorrect (may cause type errors)
basePrice: 49.99
salePrice: 39.99
```

### 3. **Keep Base Price Consistent**

- Base price = regular price customers expect
- Sale price = temporary discount
- When sale ends, remove `salePrice` (set to `null`), don't change `basePrice`

### 4. **Variant Pricing Strategy**

- **Size-based:** Larger sizes can have better per-unit pricing (bulk discount)
- **Color/Type-based:** Premium options can cost more
- **Individual control:** Each variant price is independent

### 5. **Price Updates**

- Use `setProductPrice` for regular products
- Use `updateProductVariant` for variants
- Both mutations update existing prices (no need to delete first)

---

## Common Scenarios

### Scenario 1: Simple Product Setup

**Goal:** Create a product and set its price

```graphql
# 1. Create product
mutation {
  createProduct(input: {
    name: "Lindt Excellence Dark 85%"
    brandId: 1
    categoryId: 1
    sku: "LINDT-DARK-85"
    description: "Premium dark chocolate"
    unitType: "GRAM"
    weight: "100.0"
  }) {
    success
    product { id name }
  }
}

# 2. Set price
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"
  }) {
    success
    price { basePrice effectivePrice }
  }
}
```

### Scenario 2: Product with Variants (Different Prices)

**Goal:** Create variants with varying prices

```graphql
# Create variants
mutation {
  v1: createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-500"
    optionValues: "{\"Weight\": \"500g\"}"
    price: "25.00"
    quantityInStock: 150
  }) {
    success
    variant { sku price }
  }
  
  v2: createProductVariant(input: {
    productId: 5
    sku: "COCO-WHITE-1000"
    optionValues: "{\"Weight\": \"1000g\"}"
    price: "45.00"  # Better per-gram price
    quantityInStock: 100
  }) {
    success
    variant { sku price }
  }
}
```

### Scenario 3: Put Product on Sale

**Goal:** Add a sale price to an existing product

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"      # Keep original
    salePrice: "39.99"      # Add sale price
  }) {
    success
    price {
      basePrice
      salePrice
      effectivePrice  # Will be 39.99
    }
  }
}
```

### Scenario 4: Update Price After Cost Change

**Goal:** Update base price (no sale)

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "54.99"      # New price
    salePrice: null         # No sale
  }) {
    success
    price {
      basePrice
      effectivePrice  # Will be 54.99
    }
  }
}
```

### Scenario 5: End a Sale

**Goal:** Remove sale price, keep base price

```graphql
mutation {
  setProductPrice(input: {
    productId: 1
    priceType: "RETAIL"
    basePrice: "49.99"      # Keep base price
    salePrice: null         # Remove sale
  }) {
    success
    price {
      effectivePrice  # Now equals basePrice
    }
  }
}
```

### Scenario 6: Query Products for Homepage

**Goal:** Display products with prices

```graphql
query {
  products(featured: true, limit: 8) {
    id
    name
    retailPrice           # Quick access to effective price
    images {
      image
      isPrimary
    }
    brand {
      name
    }
    prices {
      basePrice
      salePrice           # Check if on sale
      effectivePrice
    }
  }
}
```

---

## Summary

### ✅ **Key Takeaways**

1. **Two pricing systems:**
   - Regular products → `setProductPrice` mutation
   - Variants → Set price when creating variant

2. **Price components:**
   - `basePrice` - Regular price
   - `salePrice` - Optional discount (null = no sale)
   - `effectivePrice` - Auto-calculated (sale if available, else base)

3. **Querying:**
   - Use `retailPrice` for quick access (regular products)
   - Use `variants[].effectivePrice` for variant products
   - Filter with `minPrice`/`maxPrice` in `products` query

4. **Updates:**
   - Same mutations work for create/update
   - Set `salePrice: null` to remove sale
   - Set `isActive: false` to deactivate price

5. **Best practices:**
   - Always set prices after creating products
   - Use string format for decimal values in mutations
   - Keep base price consistent, only change sale price for promotions

---

## Quick Reference

### Admin Mutations

| Mutation | Purpose | Auth Required |
|----------|---------|---------------|
| `setProductPrice` | Set/update price for regular products | ✅ Yes |
| `createProductVariant` | Create variant with price | ✅ Yes |
| `updateProductVariant` | Update variant price | ✅ Yes |

### Public Queries

| Query | Field | Description |
|-------|-------|-------------|
| `product(id)` | `retailPrice` | Effective price (regular products) |
| `product(id)` | `prices[]` | All price tiers |
| `product(id)` | `variants[].effectivePrice` | Variant effective price |
| `products()` | `minPrice`/`maxPrice` | Filter by price range |
| `products()` | `sortBy: "price_asc"` | Sort by price |

---

**🎉 You're ready to manage pricing in your catalog!**

For more details on variants, see: `PRODUCT_VARIANTS_GUIDE.md`  
For admin operations, see: `ADMIN_GUIDE.md`

