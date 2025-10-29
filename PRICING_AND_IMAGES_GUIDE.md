# Pricing & Images Guide for Variants

## Quick Answers

### ✅ **Can we control the price for each variant?**
**YES!** Each variant has completely independent pricing.

### ✅ **Can a product hold more than 1 image?**
**YES!** Products can have unlimited images. Plus, each variant can have its own image too!

---

## Part 1: Variant Pricing Control

### **Each Variant Has Independent Pricing**

Every variant can have its own:
- ✅ **Base Price** (regular price)
- ✅ **Sale Price** (optional discount)
- ✅ **Currency** (AED by default)
- ✅ **Effective Price** (automatically uses sale price if available)

### **Example 1: Cocoa Butter (Bulk Discounts)**

```
Product: Cocoa Butter

Variant 1: 500g
   Price: 35.00 AED
   Per gram: 0.07 AED

Variant 2: 1kg (1000g)
   Price: 65.00 AED
   Per gram: 0.065 AED  (7% discount!)

Variant 3: 2kg (2000g)
   Price: 120.00 AED
   Per gram: 0.06 AED  (14% discount!)
```

**You control the exact price - not automatic calculation!**

### **Example 2: Food Coloring (Color Affects Price)**

```
Product: Food Coloring

Red (cheaper):
   50g: 15.00 AED
   100g: 28.00 AED

Blue (premium):
   50g: 18.00 AED
   100g: 32.00 AED

Yellow (budget):
   50g: 12.00 AED
   100g: 22.00 AED

Green (standard):
   50g: 15.00 AED
   100g: 28.00 AED
```

**Different colors = different prices!**

### **Example 3: Selective Sales**

```
Product: Coco Mass

White 500g
   Regular: 25.00 AED
   Sale: (no sale)
   Customer Pays: 25.00 AED

White 1kg
   Regular: 42.00 AED
   Sale: 39.99 AED ✨
   Customer Pays: 39.99 AED

Dark 500g
   Regular: 28.00 AED
   Sale: 24.99 AED ✨
   Customer Pays: 24.99 AED

Dark 1kg
   Regular: 50.00 AED
   Sale: (no sale)
   Customer Pays: 50.00 AED
```

**Put only specific variants on sale!**

---

## Setting Variant Prices

### **When Creating Variant**

```graphql
mutation CreateVariant($input: ProductVariantInput!) {
  createProductVariant(input: $input) {
    success
    variant {
      sku
      price
      salePrice
      effectivePrice
    }
  }
}

# Variables:
{
  "input": {
    "productId": 1,
    "sku": "COCOA-BUTTER-500",
    "optionValues": "{\"Weight\": \"500g\"}",
    "price": "35.00",          # Regular price
    "salePrice": null,         # No sale (optional)
    "currency": "AED",
    "quantityInStock": 150,
    "weight": "500"
  }
}
```

### **Updating Variant Price**

```graphql
mutation {
  updateProductVariant(
    variantId: 123
    price: "38.00"              # New regular price
    salePrice: "34.99"          # Add sale price
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

### **Remove Sale Price**

```graphql
mutation {
  updateProductVariant(
    variantId: 123
    salePrice: null             # Remove sale
  ) {
    success
  }
}
```

---

## Part 2: Multiple Images Per Product

### **Product Image System**

Each product can have:
- ✅ **Unlimited images**
- ✅ **One PRIMARY image** (main display)
- ✅ **Display order** (1st, 2nd, 3rd...)
- ✅ **Alt text** (for SEO)
- ✅ **Automatic optimization** (resized to 1200x1200, 85% quality)
- ✅ **Automatic thumbnails** (300x300)

### **Example: Product with 5 Images**

```
Product: Godiva Signature Truffles

Image 1 (PRIMARY ⭐)
   File: godiva-truffles-main.jpg
   Alt: "Godiva Signature Chocolate Truffles gift box"
   Order: 1
   
Image 2
   File: godiva-truffles-closeup.jpg
   Alt: "Close-up of Godiva truffle detail"
   Order: 2
   
Image 3
   File: godiva-truffles-back.jpg
   Alt: "Godiva truffles package back view"
   Order: 3
   
Image 4
   File: godiva-truffles-open.jpg
   Alt: "Opened Godiva truffles box interior"
   Order: 4
   
Image 5
   File: godiva-truffles-lifestyle.jpg
   Alt: "Godiva truffles served with coffee"
   Order: 5
```

---

## Uploading Multiple Images

### **Step 1: Upload First Image (Primary)**

```graphql
mutation {
  uploadProductImage(input: {
    productId: 1
    image: "base64_encoded_image_data_here"
    altText: "Main product view"
    isPrimary: true
    displayOrder: 1
  }) {
    success
    message
    productImage {
      id
      image
      isPrimary
      displayOrder
    }
  }
}
```

### **Step 2: Upload Additional Images**

```graphql
# Image 2
mutation {
  uploadProductImage(input: {
    productId: 1
    image: "base64_encoded_image_data_here"
    altText: "Product close-up"
    isPrimary: false
    displayOrder: 2
  }) {
    success
    productImage { id }
  }
}

# Image 3
mutation {
  uploadProductImage(input: {
    productId: 1
    image: "base64_encoded_image_data_here"
    altText: "Package back view"
    isPrimary: false
    displayOrder: 3
  }) {
    success
    productImage { id }
  }
}
```

### **Step 3: Change Primary Image**

```graphql
mutation {
  setPrimaryImage(imageId: 456) {
    success
    message
  }
}
```

### **Step 4: Delete an Image**

```graphql
mutation {
  deleteProductImage(imageId: 789) {
    success
    message
  }
}
```

---

## Part 3: Variant-Specific Images (BONUS!)

### **Variants Can Have Their Own Images**

This is perfect for products where color/type changes appearance!

### **Example: Food Coloring**

```
Product: Food Coloring (parent)
   └─ Image 1: Generic packaging (shared)
   └─ Image 2: All colors together (shared)

Variant: Red 50g
   └─ Variant Image: red-bottle.jpg (specific to red)

Variant: Blue 50g
   └─ Variant Image: blue-bottle.jpg (specific to blue)

Variant: Green 50g
   └─ Variant Image: green-bottle.jpg (specific to green)
```

### **How It Works**

```graphql
# Create variant WITH its own image
mutation CreateVariant($input: ProductVariantInput!) {
  createProductVariant(input: $input) {
    success
    variant {
      sku
      image  # Variant-specific image
    }
  }
}

# Variables:
{
  "input": {
    "productId": 1,
    "sku": "FOOD-COLOR-RED-50",
    "optionValues": "{\"Color\": \"Red\", \"Weight\": \"50g\"}",
    "price": "15.00",
    # Note: Variant image upload happens separately via file upload
  }
}
```

### **Frontend Display Logic**

```javascript
// When customer views product page:

if (noVariantSelected) {
  // Show parent product images
  displayImages = product.images  // All 5 images
}

if (variantSelected && variant.hasImage) {
  // Show variant-specific image FIRST
  displayImages = [variant.image, ...product.images]
}

if (variantSelected && !variant.hasImage) {
  // Show parent images
  displayImages = product.images
}
```

**Result:**
- Customer sees all parent images initially
- When they select "Red" → Red bottle image shows first
- When they select "Blue" → Blue bottle image shows first

---

## Querying Images

### **Get Product with All Images**

```graphql
query {
  product(id: 1) {
    name
    images {
      id
      image
      altText
      isPrimary
      displayOrder
    }
  }
}
```

**Response:**
```json
{
  "product": {
    "name": "Godiva Truffles",
    "images": [
      {
        "id": 1,
        "image": "/media/products/godiva-main.jpg",
        "altText": "Godiva truffles main view",
        "isPrimary": true,
        "displayOrder": 1
      },
      {
        "id": 2,
        "image": "/media/products/godiva-closeup.jpg",
        "altText": "Close-up detail",
        "isPrimary": false,
        "displayOrder": 2
      },
      // ... more images
    ]
  }
}
```

### **Get Variants with Images**

```graphql
query {
  product(id: 1) {
    name
    variants {
      sku
      price
      image  # Variant-specific image
      product {
        images {  # Parent images
          image
          isPrimary
        }
      }
    }
  }
}
```

---

## Practical Scenarios

### **Scenario 1: Cocoa Products (Weight Variants)**

**Product:** Cocoa Butter
**Variants:** 500g, 1kg, 2kg

**Images Strategy:**
- ✅ 3-4 product images (shared by all variants)
- ❌ No variant-specific images (all look the same)

**Pricing Strategy:**
```
500g:  35.00 AED (0.070 AED/g)
1kg:   65.00 AED (0.065 AED/g) - 7% discount
2kg:   120.00 AED (0.060 AED/g) - 14% discount
```

---

### **Scenario 2: Food Coloring (Color + Weight)**

**Product:** Food Coloring
**Variants:** 4 colors × 2 weights = 8 variants

**Images Strategy:**
- ✅ 2 parent images (packaging, all colors)
- ✅ 4 variant images (one per color)
- When Red selected → Show red bottle
- When Blue selected → Show blue bottle

**Pricing Strategy:**
```
Red (standard):
   50g: 15.00 AED
   100g: 28.00 AED

Blue (premium - imported):
   50g: 18.00 AED
   100g: 32.00 AED

Yellow (budget):
   50g: 12.00 AED
   100g: 22.00 AED
```

---

### **Scenario 3: Seasonal Sales**

**Product:** Coco Mass (all variants)

**Spring Sale - Only bulk sizes:**
```
White 500g: 25.00 AED (no sale)
White 1kg:  42.00 → 39.99 AED ✨
Dark 500g:  28.00 AED (no sale)
Dark 1kg:   50.00 → 45.99 AED ✨
```

**Update sale prices:**
```graphql
# Put 1kg on sale
mutation {
  updateProductVariant(variantId: 2, salePrice: "39.99") { success }
}
mutation {
  updateProductVariant(variantId: 4, salePrice: "45.99") { success }
}

# After sale ends - remove sale prices
mutation {
  updateProductVariant(variantId: 2, salePrice: null) { success }
}
mutation {
  updateProductVariant(variantId: 4, salePrice: null) { success }
}
```

---

## Image Best Practices

### **Number of Images:**
- **Minimum:** 1 image (primary)
- **Recommended:** 3-5 images
- **Maximum:** Unlimited (but 5-7 is typical)

### **What to Include:**
1. **Main product image** (PRIMARY)
2. **Close-up/detail shot**
3. **Package back view** (ingredients, info)
4. **Size comparison** (with hand or common object)
5. **Lifestyle/use case** (in use or styled)

### **Image Quality:**
- **Format:** JPG or PNG
- **Size:** System auto-resizes to 1200×1200
- **Quality:** 85% (automatic optimization)
- **Thumbnails:** 300×300 (automatic)

### **Alt Text Tips:**
```
✅ Good: "Godiva Signature Chocolate Truffles 180g gift box"
❌ Bad: "image1.jpg"

✅ Good: "Close-up of Godiva truffle showing smooth ganache center"
❌ Bad: "product"
```

---

## Summary

### **✅ Pricing Control**
- Each variant = independent price
- Set sale prices per variant
- Bulk discounts (you control exact price)
- Color/type pricing (premium colors cost more)
- Update prices anytime

### **✅ Multiple Images**
- Products = unlimited images
- One primary image
- Display order control
- SEO-friendly alt text
- Automatic optimization

### **✅ Variant Images (Bonus)**
- Variants can have own images
- Perfect for color variants
- Parent images as fallback
- Smart frontend display

### **Your System Has:**
```
Regular Products:
   ├─ Multiple images ✅
   └─ One price ✅

Variant Products:
   ├─ Multiple parent images ✅
   └─ Variants:
       ├─ Independent pricing ✅
       ├─ Sale prices ✅
       ├─ Optional own image ✅
       └─ Fallback to parent images ✅
```

**Everything you need for a professional chocolate e-commerce store! 🍫**

