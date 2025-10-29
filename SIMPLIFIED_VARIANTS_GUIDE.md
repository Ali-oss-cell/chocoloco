# Simplified Product Variants Guide
## For Your Chocolate Store

Based on manager requirements:
- ✅ **Weight variants** for most products
- ✅ **Color variants** only for specific products (food coloring, cocoa mass)

---

## 3 Product Types in Your Store

### 1️⃣ **Weight-Only Variants** (Most Common)
Products that come in different weights but same type.

### 2️⃣ **Weight + Color Variants** (Special Cases)
Products like food coloring that have both color and weight options.

### 3️⃣ **No Variants** (Fixed Products)
Pre-packaged items with fixed size (gift boxes, branded chocolates).

---

## TYPE 1: Weight-Only Variants

### **Example: Cocoa Butter**

**Product:** Cocoa Butter
**Weights:** 500g, 1kg, 2kg

#### Step-by-Step:

```graphql
# 1. Create parent product
mutation {
  createProduct(input: {
    sku: "COCOA-BUTTER"
    name: "Cocoa Butter"
    slug: "cocoa-butter"
    brandId: 1
    categoryId: 1
    description: "Premium cocoa butter"
    unitType: "GRAM"
  }) {
    success
    product { id }
  }
}
```

```graphql
# 2. Create weight options
mutation {
  createVariantOptions(
    productId: 22
    options: [{
      name: "Weight"
      values: ["500g", "1kg", "2kg"]
    }]
  ) {
    success
  }
}
```

```graphql
# 3. Create each variant
mutation CreateVariant($input: ProductVariantInput!) {
  createProductVariant(input: $input) {
    success
    variant { sku price }
  }
}

# Variables for 500g:
{
  "input": {
    "productId": 22,
    "sku": "COCOA-BUTTER-500",
    "optionValues": "{\"Weight\": \"500g\"}",
    "price": "35.00",
    "quantityInStock": 150,
    "weight": "500",
    "isDefault": true
  }
}

# Variables for 1kg:
{
  "input": {
    "productId": 22,
    "sku": "COCOA-BUTTER-1000",
    "optionValues": "{\"Weight\": \"1kg\"}",
    "price": "65.00",
    "quantityInStock": 100,
    "weight": "1000",
    "isDefault": false
  }
}

# Variables for 2kg:
{
  "input": {
    "productId": 22,
    "sku": "COCOA-BUTTER-2000",
    "optionValues": "{\"Weight\": \"2kg\"}",
    "price": "120.00",
    "quantityInStock": 50,
    "weight": "2000",
    "isDefault": false
  }
}
```

**Result:**
```
Product: Cocoa Butter
└── Select Weight: [○ 500g] [○ 1kg] [○ 2kg]

COCOA-BUTTER-500: 500g - 35.00 AED (150 in stock) ⭐ DEFAULT
COCOA-BUTTER-1000: 1kg - 65.00 AED (100 in stock)
COCOA-BUTTER-2000: 2kg - 120.00 AED (50 in stock)
```

---

## TYPE 2: Weight + Color Variants

### **Example: Food Coloring**

**Product:** Food Coloring
**Colors:** Red, Blue, Green, Yellow
**Weights:** 50g, 100g

**Total Combinations:** 8 variants (4 colors × 2 weights)

#### Step-by-Step:

```graphql
# 1. Create parent product
mutation {
  createProduct(input: {
    sku: "FOOD-COLOR"
    name: "Food Coloring"
    slug: "food-coloring"
    brandId: 1
    categoryId: 5
    description: "Professional food coloring for chocolate decoration"
    unitType: "GRAM"
  }) {
    success
    product { id }
  }
}
```

```graphql
# 2. Create color + weight options
mutation {
  createVariantOptions(
    productId: 23
    options: [
      {
        name: "Color"
        values: ["Red", "Blue", "Green", "Yellow"]
        displayOrder: 0
      },
      {
        name: "Weight"
        values: ["50g", "100g"]
        displayOrder: 1
      }
    ]
  ) {
    success
  }
}
```

```graphql
# 3. Create variants (8 total)
mutation CreateVariant($input: ProductVariantInput!) {
  createProductVariant(input: $input) {
    success
    variant { sku }
  }
}

# Example variables for Red 50g:
{
  "input": {
    "productId": 23,
    "sku": "FOOD-COLOR-RED-50",
    "optionValues": "{\"Color\": \"Red\", \"Weight\": \"50g\"}",
    "price": "15.00",
    "quantityInStock": 100,
    "weight": "50",
    "isDefault": true
  }
}

# Repeat for all 8 combinations:
# FOOD-COLOR-RED-50
# FOOD-COLOR-RED-100
# FOOD-COLOR-BLUE-50
# FOOD-COLOR-BLUE-100
# FOOD-COLOR-GREEN-50
# FOOD-COLOR-GREEN-100
# FOOD-COLOR-YELLOW-50
# FOOD-COLOR-YELLOW-100
```

**Result:**
```
Product: Food Coloring
├── Select Color: [○ Red] [○ Blue] [○ Green] [○ Yellow]
└── Select Weight: [○ 50g] [○ 100g]

Red 50g - 15.00 AED
Red 100g - 28.00 AED
Blue 50g - 15.00 AED
Blue 100g - 28.00 AED
Green 50g - 15.00 AED
Green 100g - 28.00 AED
Yellow 50g - 15.00 AED
Yellow 100g - 28.00 AED
```

---

## TYPE 3: No Variants (Regular Products)

### **Example: Godiva Truffles**

For fixed products that don't need variants:

```graphql
mutation {
  createProduct(input: {
    sku: "GODIVA-TRUFFLE-180"
    name: "Godiva Signature Chocolate Truffles 180g"
    slug: "godiva-truffle-180g"
    brandId: 2
    categoryId: 3
    description: "Luxurious chocolate truffles"
    weight: 180
    unitType: "GRAM"
  }) {
    success
    product { id }
  }
}

# Then set price and inventory normally (no variants)
setProductPrice(input: {
  productId: 1
  priceType: "RETAIL"
  basePrice: "55.00"
})

updateInventory(input: {
  productId: 1
  quantityInStock: 500
})
```

**Result:**
```
Product: Godiva Signature Chocolate Truffles 180g
Price: 55.00 AED
Stock: 500 units
(No variant selector - fixed product)
```

---

## Quick Reference: Common Products

### **Products with Weight Variants Only:**

1. **Cocoa Mass Dark**
   - 500g, 1kg, 2kg

2. **Cocoa Mass White**
   - 500g, 1kg, 2kg

3. **Cocoa Butter**
   - 500g, 1kg, 2kg

4. **Cocoa Powder**
   - 250g, 500g, 1kg

5. **Chocolate Chips**
   - 250g, 500g, 1kg

6. **Chocolate Bars (Generic)**
   - 100g, 200g, 400g

### **Products with Color + Weight:**

1. **Food Coloring**
   - Colors: Red, Blue, Green, Yellow
   - Weights: 50g, 100g

2. **Cocoa Mass (if both colors)**
   - Colors: White, Dark
   - Weights: 500g, 1kg, 2kg

### **Products without Variants:**

1. **Branded Gift Boxes**
   - Fixed size, fixed content

2. **Pre-packaged Branded Items**
   - Lindt Excellence 100g (fixed)
   - Ferrero Rocher 16pcs (fixed)
   - Toblerone 100g (fixed)

---

## Practical Workflow

### **Decision Tree:**

```
Does the product come in different sizes?
│
├─ NO → Create as regular product (no variants)
│
└─ YES → Does it also have different colors/types?
    │
    ├─ NO → Create weight-only variants
    │
    └─ YES → Create weight + color variants
```

### **Example Decisions:**

| Product | Has Size? | Has Color? | Solution |
|---------|-----------|------------|----------|
| Cocoa Butter | ✅ Yes | ❌ No | Weight variants |
| Food Coloring | ✅ Yes | ✅ Yes | Weight + Color |
| Godiva Box | ❌ No | ❌ No | No variants |
| Chocolate Chips | ✅ Yes | ❌ No | Weight variants |
| Cocoa Mass | ✅ Yes | ✅ Yes (White/Dark) | Weight + Color |

---

## SKU Naming Convention

### **For Weight-Only:**
```
{PRODUCT}-{WEIGHT}

Examples:
COCOA-BUTTER-500
COCOA-BUTTER-1000
COCOA-POWDER-250
```

### **For Weight + Color:**
```
{PRODUCT}-{COLOR}-{WEIGHT}

Examples:
FOOD-COLOR-RED-50
FOOD-COLOR-BLUE-100
COCO-MASS-WHITE-500
COCO-MASS-DARK-1000
```

### **For No Variants:**
```
{BRAND}-{PRODUCT}-{SIZE}

Examples:
GODIVA-TRUFFLE-180
LINDT-EXCELLENCE-100
FERRERO-ROCHER-16
```

---

## Common Weights to Use

### **Small Items (Coloring, Additives):**
- 50g, 100g, 200g

### **Medium Items (Cocoa Products):**
- 250g, 500g, 1kg

### **Large Items (Bulk Chocolate):**
- 1kg, 2kg, 5kg

### **Bars and Tablets:**
- 100g, 200g, 400g

---

## Frontend Display Examples

### **Weight-Only Selector:**
```
Product: Cocoa Butter
Price: Starting from 35.00 AED

Select Weight:
┌─────┐ ┌─────┐ ┌─────┐
│ 500g│ │ 1kg │ │ 2kg │
└─────┘ └─────┘ └─────┘
  ✓       

Selected: 500g
Price: 35.00 AED
Stock: 150 units (In Stock)
SKU: COCOA-BUTTER-500

[Add to Cart]
```

### **Weight + Color Selector:**
```
Product: Food Coloring
Price: Starting from 15.00 AED

Select Color:
┌─────┐ ┌─────┐ ┌──────┐ ┌───────┐
│ Red │ │Blue │ │Green │ │Yellow │
└─────┘ └─────┘ └──────┘ └───────┘
  ✓

Select Weight:
┌─────┐ ┌──────┐
│ 50g │ │ 100g │
└─────┘ └──────┘
  ✓

Selected: Red, 50g
Price: 15.00 AED
Stock: 100 units (In Stock)
SKU: FOOD-COLOR-RED-50

[Add to Cart]
```

---

## Summary

### **Your Store Has 3 Product Types:**

1. **Weight Variants (Most Products)**
   - Cocoa products, chocolate chips, powder
   - Simple dropdown: Select Weight

2. **Weight + Color Variants (Special Items)**
   - Food coloring, cocoa mass (white/dark)
   - Two dropdowns: Select Color, Select Weight

3. **No Variants (Branded Items)**
   - Gift boxes, pre-packaged branded chocolates
   - Direct "Add to Cart"

### **System Supports All Three:**
✅ Flexible - Use variants when needed
✅ Simple - Regular products when variants not needed
✅ Professional - Matches industry standards

**Your variant system is ready to use! Start with your most common products that need weight variants.** 🍫

