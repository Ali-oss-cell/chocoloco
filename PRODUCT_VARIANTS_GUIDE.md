# Product Variants System Guide

## Overview

The Product Variants System allows you to create products with multiple options (like color, weight, size) that customers can choose from. Instead of creating separate products, you create one parent product with multiple variants.

## Example: Coco Mass

**Parent Product:** Coco Mass
**Variant Options:**
- Color: White, Dark
- Weight: 500g, 1000g

**Result:** 4 variants
1. White Coco Mass 500g
2. White Coco Mass 1000g
3. Dark Coco Mass 500g
4. Dark Coco Mass 1000g

Each variant has its own:
- SKU
- Price (with optional sale price)
- Inventory (stock levels)
- Weight

---

## How It Works

### Database Structure

```
Product (Parent)
  ├── ProductVariantOption (Color)
  │   ├── ProductVariantOptionValue (White)
  │   └── ProductVariantOptionValue (Dark)
  │
  ├── ProductVariantOption (Weight)
  │   ├── ProductVariantOptionValue (500g)
  │   └── ProductVariantOptionValue (1000g)
  │
  └── ProductVariant (Actual variants)
      ├── COCO-WHITE-500 (Color: White, Weight: 500g)
      ├── COCO-WHITE-1000 (Color: White, Weight: 1000g)
      ├── COCO-DARK-500 (Color: Dark, Weight: 500g)
      └── COCO-DARK-1000 (Color: Dark, Weight: 1000g)
```

---

## Step-by-Step Implementation

### Step 1: Create Parent Product

```graphql
mutation {
  createProduct(input: {
    sku: "COCO-MASS"
    name: "Coco Mass"
    slug: "coco-mass"
    brandId: 1
    categoryId: 1
    description: "Premium coco mass available in multiple variants"
    unitType: "GRAM"
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

### Step 2: Create Variant Options

```graphql
mutation {
  createVariantOptions(
    productId: 21
    options: [
      {
        name: "Color"
        values: ["White", "Dark"]
        displayOrder: 0
      },
      {
        name: "Weight"
        values: ["500g", "1000g"]
        displayOrder: 1
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

### Step 3: Create Individual Variants

```graphql
mutation CreateVariant($input: ProductVariantInput!) {
  createProductVariant(input: $input) {
    success
    message
    variant {
      id
      sku
      price
      salePrice
      quantityInStock
      optionValues {
        value
      }
    }
  }
}

# Variables:
{
  "input": {
    "productId": 21,
    "sku": "COCO-WHITE-500",
    "optionValues": "{\"Color\": \"White\", \"Weight\": \"500g\"}",
    "price": "25.00",
    "quantityInStock": 150,
    "weight": "500",
    "isDefault": true
  }
}
```

**Repeat for all 4 variants:**

1. **COCO-WHITE-500**: White, 500g - 25.00 AED
2. **COCO-WHITE-1000**: White, 1000g - 45.00 AED (Sale: 39.99 AED)
3. **COCO-DARK-500**: Dark, 500g - 28.00 AED
4. **COCO-DARK-1000**: Dark, 1000g - 50.00 AED

---

## Querying Products with Variants

### Get Product with All Variants

```graphql
query {
  product(id: 21) {
    id
    name
    sku
    description
    hasVariants
    
    # Variant options (Color, Weight, etc.)
    variantOptions {
      id
      name
      displayOrder
      values {
        id
        value
        displayOrder
      }
    }
    
    # Actual variants
    variants {
      id
      sku
      price
      salePrice
      effectivePrice
      quantityInStock
      availableQuantity
      isInStock
      isLowStock
      isDefault
      weight
      optionValues {
        value
      }
    }
  }
}
```

### Search Products (Returns Parent Products)

```graphql
query {
  searchProducts(query: "coco") {
    name
    sku
    hasVariants
    variants {
      sku
      price
      effectivePrice
      isInStock
      optionValues {
        value
      }
    }
  }
}
```

---

## Managing Variants

### Update Variant (Price, Stock, etc.)

```graphql
mutation {
  updateProductVariant(
    variantId: 1
    price: "42.00"
    salePrice: "38.99"
    quantityInStock: 80
    isActive: true
    isDefault: false
  ) {
    success
    message
    variant {
      sku
      price
      salePrice
      effectivePrice
      quantityInStock
    }
  }
}
```

### Delete a Variant

```graphql
mutation {
  deleteProductVariant(variantId: 1) {
    success
    message
  }
}
```

---

## Frontend Implementation

### Product Page Display

```javascript
// Product page should display:
1. Parent product info (name, description, images)
2. Variant selector dropdowns:
   - Color: [○ White] [○ Dark]
   - Weight: [○ 500g] [○ 1000g]
3. Selected variant details:
   - Price: 25.00 AED
   - Stock: 150 units (In Stock)
   - SKU: COCO-WHITE-500
4. Add to Cart button (uses variant SKU)
```

### Variant Selector Logic

```javascript
// When user selects options:
selectedColor = "White"
selectedWeight = "500g"

// Find matching variant:
variant = product.variants.find(v => 
  v.optionValues.includes("White") && 
  v.optionValues.includes("500g")
)

// Display variant info:
price = variant.effectivePrice
stock = variant.quantityInStock
sku = variant.sku
inStock = variant.isInStock
```

### Add to Cart

```javascript
// When adding to cart, use variant SKU
addToCart({
  variantSku: "COCO-WHITE-500",
  quantity: 2
})
```

---

## Benefits of Variant System

### ✅ Advantages:

1. **Clean Product Catalog**: 1 product listing instead of 4
2. **Better UX**: Customer selects options on one page
3. **Easier Management**: Update parent product once
4. **Flexible**: Add new options/values easily
5. **Professional**: Standard e-commerce approach
6. **SEO Friendly**: One URL per product family

### 📊 Comparison:

| Feature | Separate Products | Variant System |
|---------|-------------------|----------------|
| Product Listings | 4 separate | 1 parent |
| Management | Update 4 times | Update once |
| Customer UX | Browse 4 products | Select options |
| URL Structure | 4 different URLs | 1 URL with selector |
| Search Results | Shows all 4 | Shows 1 with options |
| Professional | Basic | Professional |

---

## Common Use Cases

### 1. Chocolate Products with Sizes

```
Product: Lindt Excellence Dark Chocolate
Options:
  - Percentage: [70%, 85%, 90%]
  - Size: [100g, 200g]
Result: 6 variants
```

### 2. Gift Boxes with Piece Count

```
Product: Ferrero Rocher Gift Box
Options:
  - Pieces: [16, 24, 48]
Result: 3 variants
```

### 3. Chocolate Bars with Flavors

```
Product: Toblerone Bar
Options:
  - Flavor: [Milk, Dark, White]
  - Size: [100g, 200g, 400g]
Result: 9 variants
```

### 4. Coco Mass (Your Example)

```
Product: Coco Mass
Options:
  - Color: [White, Dark]
  - Weight: [500g, 1000g]
Result: 4 variants
```

---

## API Reference

### Queries

```graphql
# Get product with variants
product(id: Int, slug: String): ProductType

# Check if product has variants
product { hasVariants }

# Get variant options
product { variantOptions { name values { value } } }

# Get all variants
product { variants { sku price optionValues { value } } }
```

### Mutations

```graphql
# Create variant options
createVariantOptions(
  productId: Int!
  options: [VariantOptionInput!]!
): CreateVariantOptionsResponse

# Create variant
createProductVariant(
  input: ProductVariantInput!
): CreateProductVariantResponse

# Update variant
updateProductVariant(
  variantId: Int!
  price: Decimal
  salePrice: Decimal
  quantityInStock: Int
  isActive: Boolean
  isDefault: Boolean
): UpdateProductVariantResponse

# Delete variant
deleteProductVariant(
  variantId: Int!
): DeleteProductVariantResponse
```

---

## Best Practices

### 1. Always Set a Default Variant
```graphql
isDefault: true  # First or most popular variant
```

### 2. Use Clear Option Names
```
✅ Good: "Color", "Weight", "Size"
❌ Bad: "Option1", "Type", "Kind"
```

### 3. Consistent Value Format
```
✅ Good: "500g", "1000g", "2000g"
❌ Bad: "500g", "1kg", "2 kilograms"
```

### 4. Logical Display Order
```
displayOrder: 0  # Color (first)
displayOrder: 1  # Weight (second)
displayOrder: 2  # Size (third)
```

### 5. Set Low Stock Thresholds
```graphql
lowStockThreshold: 10  # Alert when < 10 units
```

---

## Troubleshooting

### Issue: "Option not found"
**Solution**: Create variant options before creating variants

### Issue: "SKU already exists"
**Solution**: Use unique SKUs for each variant

### Issue: Variant not showing
**Solution**: Check `isActive: true` on variant

### Issue: Wrong default variant
**Solution**: Only one variant should have `isDefault: true`

---

## Next Steps

1. ✅ Create parent products
2. ✅ Add variant options
3. ✅ Create all variants
4. ⏳ Build frontend variant selector
5. ⏳ Update cart to handle variants
6. ⏳ Update order system for variants

---

## Summary

The Product Variants System gives you a professional e-commerce solution for products with multiple options. It's perfect for your chocolate store where products come in different sizes, colors, or configurations.

**Your Coco Mass example is now live with 4 variants! 🎉**

