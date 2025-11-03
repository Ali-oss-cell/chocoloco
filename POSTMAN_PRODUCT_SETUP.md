# 🍫 Complete Product Setup for Postman

**Use this guide to add 5 Categories, 5 Brands, and 20 Products to your store.**

**⚠️ IMPORTANT:** Make sure you're authenticated first! Run "Login - Get JWT Token" from the Postman collection and save the token.

---

## 📋 Step-by-Step Guide

### STEP 1: Create 5 Categories

**In Postman:** Use `🔐 Authentication` → Login first, then use `🛍️ Mutations - Admin - Categories` → Create Category

```graphql
mutation {
  cat1: createCategory(input: {
    name: "Dark Chocolate"
    slug: "dark-chocolate"
    description: "Premium dark chocolate selection"
    isActive: true
    displayOrder: 1
  }) {
    success
    category { id name }
  }
  
  cat2: createCategory(input: {
    name: "Milk Chocolate"
    slug: "milk-chocolate"
    description: "Smooth and creamy milk chocolate"
    isActive: true
    displayOrder: 2
  }) {
    success
    category { id name }
  }
  
  cat3: createCategory(input: {
    name: "White Chocolate"
    slug: "white-chocolate"
    description: "Delicate white chocolate varieties"
    isActive: true
    displayOrder: 3
  }) {
    success
    category { id name }
  }
  
  cat4: createCategory(input: {
    name: "Chocolate Bars"
    slug: "chocolate-bars"
    description: "Classic chocolate bars"
    isActive: true
    displayOrder: 4
  }) {
    success
    category { id name }
  }
  
  cat5: createCategory(input: {
    name: "Chocolate Gifts"
    slug: "chocolate-gifts"
    description: "Premium gift boxes and assortments"
    isActive: true
    displayOrder: 5
  }) {
    success
    category { id name }
  }
}
```

**✅ Save the category IDs:** You'll need them (should be 1, 2, 3, 4, 5)

---

### STEP 2: Create 5 Brands

**In Postman:** Use `🏭 Mutations - Admin - Brands` → Create Brand

```graphql
mutation {
  brand1: createBrand(input: {
    name: "Lindt"
    slug: "lindt"
    description: "Swiss chocolate excellence since 1845"
    countryOfOrigin: "Switzerland"
    isActive: true
    displayOrder: 1
  }) {
    success
    brand { id name }
  }
  
  brand2: createBrand(input: {
    name: "Godiva"
    slug: "godiva"
    description: "Belgian chocolate artisans since 1926"
    countryOfOrigin: "Belgium"
    isActive: true
    displayOrder: 2
  }) {
    success
    brand { id name }
  }
  
  brand3: createBrand(input: {
    name: "Ferrero Rocher"
    slug: "ferrero-rocher"
    description: "Italian luxury chocolate"
    countryOfOrigin: "Italy"
    isActive: true
    displayOrder: 3
  }) {
    success
    brand { id name }
  }
  
  brand4: createBrand(input: {
    name: "Toblerone"
    slug: "toblerone"
    description: "Iconic Swiss chocolate with honey and almond"
    countryOfOrigin: "Switzerland"
    isActive: true
    displayOrder: 4
  }) {
    success
    brand { id name }
  }
  
  brand5: createBrand(input: {
    name: "Cadbury"
    slug: "cadbury"
    description: "British chocolate tradition"
    countryOfOrigin: "United Kingdom"
    isActive: true
    displayOrder: 5
  }) {
    success
    brand { id name }
  }
}
```

**✅ Save the brand IDs:** You'll need them (should be 1, 2, 3, 4, 5)

**Note:** 
- Category ID 1 = Dark Chocolate
- Category ID 2 = Milk Chocolate
- Category ID 3 = White Chocolate
- Category ID 4 = Chocolate Bars
- Category ID 5 = Chocolate Gifts

- Brand ID 1 = Lindt
- Brand ID 2 = Godiva
- Brand ID 3 = Ferrero Rocher
- Brand ID 4 = Toblerone
- Brand ID 5 = Cadbury

---

### STEP 3: Create 20 Products (4 batches of 5)

**In Postman:** Use `📦 Mutations - Admin - Products` → Create Product

#### Batch 1: Products 1-5 (Lindt Dark Chocolates)

```graphql
mutation {
  p1: createProduct(input: {
    sku: "LINDT-DARK-85"
    name: "Lindt Excellence Dark 85%"
    slug: "lindt-excellence-dark-85"
    brandId: 1
    categoryId: 1
    description: "Intense dark chocolate with 85% cocoa content"
    shortDescription: "Premium dark chocolate bar"
    weight: 100.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p2: createProduct(input: {
    sku: "LINDT-DARK-70"
    name: "Lindt Excellence Dark 70%"
    slug: "lindt-excellence-dark-70"
    brandId: 1
    categoryId: 1
    description: "Smooth dark chocolate with 70% cocoa"
    shortDescription: "Rich dark chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p3: createProduct(input: {
    sku: "LINDT-SEA-SALT"
    name: "Lindt Dark Sea Salt"
    slug: "lindt-dark-sea-salt"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate with a touch of sea salt"
    shortDescription: "Salted dark chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
  
  p4: createProduct(input: {
    sku: "LINDT-ORANGE"
    name: "Lindt Dark Orange Intense"
    slug: "lindt-dark-orange"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate with natural orange flavor"
    shortDescription: "Orange dark chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
  
  p5: createProduct(input: {
    sku: "LINDT-MINT"
    name: "Lindt Dark Mint Intense"
    slug: "lindt-dark-mint"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate with refreshing mint"
    shortDescription: "Mint dark chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
}
```

#### Batch 2: Products 6-10 (Lindt Milk & White)

```graphql
mutation {
  p6: createProduct(input: {
    sku: "LINDT-MILK-001"
    name: "Lindt Milk Chocolate Classic"
    slug: "lindt-milk-classic"
    brandId: 1
    categoryId: 2
    description: "Smooth and creamy milk chocolate"
    shortDescription: "Classic milk chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p7: createProduct(input: {
    sku: "LINDT-MILK-HAZEL"
    name: "Lindt Milk Chocolate with Hazelnuts"
    slug: "lindt-milk-hazelnut"
    brandId: 1
    categoryId: 2
    description: "Creamy milk chocolate with whole hazelnuts"
    shortDescription: "Milk chocolate with hazelnuts"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
  
  p8: createProduct(input: {
    sku: "LINDT-WHITE-001"
    name: "Lindt White Chocolate"
    slug: "lindt-white-chocolate"
    brandId: 1
    categoryId: 3
    description: "Delicate white chocolate"
    shortDescription: "Smooth white chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
  
  p9: createProduct(input: {
    sku: "LINDT-LINDOR-MILK"
    name: "Lindt Lindor Milk Chocolate Truffles"
    slug: "lindt-lindor-milk"
    brandId: 1
    categoryId: 2
    description: "Irresistibly smooth melting truffles"
    shortDescription: "Melting milk chocolate truffles"
    weight: 200.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p10: createProduct(input: {
    sku: "LINDT-LINDOR-DARK"
    name: "Lindt Lindor Dark Chocolate Truffles"
    slug: "lindt-lindor-dark"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate truffles with smooth filling"
    shortDescription: "Melting dark chocolate truffles"
    weight: 200.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
}
```

#### Batch 3: Products 11-15 (Other Brands)

```graphql
mutation {
  p11: createProduct(input: {
    sku: "GODIVA-DARK-001"
    name: "Godiva Dark Chocolate Bar 72%"
    slug: "godiva-dark-72"
    brandId: 2
    categoryId: 1
    description: "Belgian dark chocolate masterpiece"
    shortDescription: "Premium Belgian dark chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p12: createProduct(input: {
    sku: "FERRERO-BOX-16"
    name: "Ferrero Rocher Collection 16 pieces"
    slug: "ferrero-rocher-16"
    brandId: 3
    categoryId: 5
    description: "Luxury hazelnut chocolates in gold foil"
    shortDescription: "Premium hazelnut chocolates"
    weight: 200.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p13: createProduct(input: {
    sku: "TOBLERONE-MILK-100"
    name: "Toblerone Milk Chocolate"
    slug: "toblerone-milk-100"
    brandId: 4
    categoryId: 4
    description: "Swiss milk chocolate with honey and almond nougat"
    shortDescription: "Swiss chocolate triangle"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
  
  p14: createProduct(input: {
    sku: "TOBLERONE-DARK-100"
    name: "Toblerone Dark Chocolate"
    slug: "toblerone-dark-100"
    brandId: 4
    categoryId: 4
    description: "Swiss dark chocolate with honey and almond"
    shortDescription: "Dark Swiss chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
  
  p15: createProduct(input: {
    sku: "TOBLERONE-WHITE-100"
    name: "Toblerone White Chocolate"
    slug: "toblerone-white-100"
    brandId: 4
    categoryId: 4
    description: "White chocolate with honey and almond nougat"
    shortDescription: "White Swiss chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
  }) { success product { id name } }
}
```

#### Batch 4: Products 16-20 (More Variety)

```graphql
mutation {
  p16: createProduct(input: {
    sku: "CADBURY-DAIRY-MILK"
    name: "Cadbury Dairy Milk Chocolate"
    slug: "cadbury-dairy-milk"
    brandId: 5
    categoryId: 2
    description: "Classic British milk chocolate"
    shortDescription: "Classic British chocolate"
    weight: 100.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p17: createProduct(input: {
    sku: "GODIVA-GIFT-BOX"
    name: "Godiva Chocolate Gift Box Assortment"
    slug: "godiva-gift-box"
    brandId: 2
    categoryId: 5
    description: "Premium Belgian chocolate assortment"
    shortDescription: "Belgian chocolate gift box"
    weight: 250.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p18: createProduct(input: {
    sku: "LINDT-SWISS-LUXURY"
    name: "Lindt Swiss Luxury Selection"
    slug: "lindt-swiss-luxury"
    brandId: 1
    categoryId: 5
    description: "Assorted Swiss chocolates in premium box"
    shortDescription: "Premium Swiss assortment"
    weight: 230.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p19: createProduct(input: {
    sku: "FERRERO-BOX-24"
    name: "Ferrero Rocher Collection 24 pieces"
    slug: "ferrero-rocher-24"
    brandId: 3
    categoryId: 5
    description: "Large luxury hazelnut chocolate gift box"
    shortDescription: "Large Ferrero gift box"
    weight: 300.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
  
  p20: createProduct(input: {
    sku: "GODIVA-TRUFFLE-ASST"
    name: "Godiva Signature Chocolate Truffles"
    slug: "godiva-truffle-assortment"
    brandId: 2
    categoryId: 5
    description: "Handcrafted Belgian chocolate truffles"
    shortDescription: "Premium Belgian truffles"
    weight: 180.0
    unitType: GRAMS
    isActive: true
    featured: true
  }) { success product { id name } }
}
```

---

### STEP 4: Set Prices for All Products

**In Postman:** Use `📦 Mutations - Admin - Products` → Set Product Price (Retail)

```graphql
mutation {
  # Products 1-5: Lindt Dark (AED 45-55)
  pr1: setProductPrice(input: {productId: 1, priceType: RETAIL, basePrice: 55.00, salePrice: 49.99, minQuantity: 1, isActive: true}) { success message }
  pr2: setProductPrice(input: {productId: 2, priceType: RETAIL, basePrice: 50.00, salePrice: 44.99, minQuantity: 1, isActive: true}) { success message }
  pr3: setProductPrice(input: {productId: 3, priceType: RETAIL, basePrice: 52.00, salePrice: 46.99, minQuantity: 1, isActive: true}) { success message }
  pr4: setProductPrice(input: {productId: 4, priceType: RETAIL, basePrice: 48.00, minQuantity: 1, isActive: true}) { success message }
  pr5: setProductPrice(input: {productId: 5, priceType: RETAIL, basePrice: 48.00, minQuantity: 1, isActive: true}) { success message }
  
  # Products 6-10: Lindt Milk/White (AED 35-65)
  pr6: setProductPrice(input: {productId: 6, priceType: RETAIL, basePrice: 42.00, salePrice: 37.99, minQuantity: 1, isActive: true}) { success message }
  pr7: setProductPrice(input: {productId: 7, priceType: RETAIL, basePrice: 45.00, minQuantity: 1, isActive: true}) { success message }
  pr8: setProductPrice(input: {productId: 8, priceType: RETAIL, basePrice: 40.00, minQuantity: 1, isActive: true}) { success message }
  pr9: setProductPrice(input: {productId: 9, priceType: RETAIL, basePrice: 68.00, salePrice: 59.99, minQuantity: 1, isActive: true}) { success message }
  pr10: setProductPrice(input: {productId: 10, priceType: RETAIL, basePrice: 65.00, minQuantity: 1, isActive: true}) { success message }
  
  # Products 11-15: Other brands (AED 45-85)
  pr11: setProductPrice(input: {productId: 11, priceType: RETAIL, basePrice: 75.00, salePrice: 69.99, minQuantity: 1, isActive: true}) { success message }
  pr12: setProductPrice(input: {productId: 12, priceType: RETAIL, basePrice: 85.00, salePrice: 79.99, minQuantity: 1, isActive: true}) { success message }
  pr13: setProductPrice(input: {productId: 13, priceType: RETAIL, basePrice: 38.00, minQuantity: 1, isActive: true}) { success message }
  pr14: setProductPrice(input: {productId: 14, priceType: RETAIL, basePrice: 40.00, minQuantity: 1, isActive: true}) { success message }
  pr15: setProductPrice(input: {productId: 15, priceType: RETAIL, basePrice: 38.00, minQuantity: 1, isActive: true}) { success message }
  
  # Products 16-20: More variety (AED 35-120)
  pr16: setProductPrice(input: {productId: 16, priceType: RETAIL, basePrice: 35.00, salePrice: 29.99, minQuantity: 1, isActive: true}) { success message }
  pr17: setProductPrice(input: {productId: 17, priceType: RETAIL, basePrice: 125.00, salePrice: 109.99, minQuantity: 1, isActive: true}) { success message }
  pr18: setProductPrice(input: {productId: 18, priceType: RETAIL, basePrice: 95.00, salePrice: 84.99, minQuantity: 1, isActive: true}) { success message }
  pr19: setProductPrice(input: {productId: 19, priceType: RETAIL, basePrice: 145.00, salePrice: 129.99, minQuantity: 1, isActive: true}) { success message }
  pr20: setProductPrice(input: {productId: 20, priceType: RETAIL, basePrice: 88.00, salePrice: 79.99, minQuantity: 1, isActive: true}) { success message }
}
```

---

### STEP 5: Set Inventory for All Products

**In Postman:** Use `📦 Mutations - Admin - Products` → Update Inventory

```graphql
mutation {
  inv1: updateInventory(input: {productId: 1, quantityInStock: 500, lowStockThreshold: 50}) { success message }
  inv2: updateInventory(input: {productId: 2, quantityInStock: 450, lowStockThreshold: 50}) { success message }
  inv3: updateInventory(input: {productId: 3, quantityInStock: 300, lowStockThreshold: 30}) { success message }
  inv4: updateInventory(input: {productId: 4, quantityInStock: 250, lowStockThreshold: 30}) { success message }
  inv5: updateInventory(input: {productId: 5, quantityInStock: 250, lowStockThreshold: 30}) { success message }
  inv6: updateInventory(input: {productId: 6, quantityInStock: 600, lowStockThreshold: 60}) { success message }
  inv7: updateInventory(input: {productId: 7, quantityInStock: 400, lowStockThreshold: 40}) { success message }
  inv8: updateInventory(input: {productId: 8, quantityInStock: 350, lowStockThreshold: 35}) { success message }
  inv9: updateInventory(input: {productId: 9, quantityInStock: 200, lowStockThreshold: 25}) { success message }
  inv10: updateInventory(input: {productId: 10, quantityInStock: 180, lowStockThreshold: 25}) { success message }
  inv11: updateInventory(input: {productId: 11, quantityInStock: 300, lowStockThreshold: 30}) { success message }
  inv12: updateInventory(input: {productId: 12, quantityInStock: 150, lowStockThreshold: 20}) { success message }
  inv13: updateInventory(input: {productId: 13, quantityInStock: 400, lowStockThreshold: 40}) { success message }
  inv14: updateInventory(input: {productId: 14, quantityInStock: 350, lowStockThreshold: 35}) { success message }
  inv15: updateInventory(input: {productId: 15, quantityInStock: 300, lowStockThreshold: 30}) { success message }
  inv16: updateInventory(input: {productId: 16, quantityInStock: 800, lowStockThreshold: 80}) { success message }
  inv17: updateInventory(input: {productId: 17, quantityInStock: 100, lowStockThreshold: 15}) { success message }
  inv18: updateInventory(input: {productId: 18, quantityInStock: 120, lowStockThreshold: 15}) { success message }
  inv19: updateInventory(input: {productId: 19, quantityInStock: 80, lowStockThreshold: 10}) { success message }
  inv20: updateInventory(input: {productId: 20, quantityInStock: 90, lowStockThreshold: 12}) { success message }
}
```

---

### STEP 6: Verify Everything Works

**In Postman:** Use `📊 Queries - Products` → Get All Products

```graphql
query {
  products(limit: 25) {
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
      isInStock
    }
  }
}
```

---

## ✅ Summary

After completing all steps, you'll have:

- ✅ **5 Categories** (Dark, Milk, White, Bars, Gifts)
- ✅ **5 Brands** (Lindt, Godiva, Ferrero, Toblerone, Cadbury)
- ✅ **20 Products** with full details
- ✅ **All prices set** (AED 29.99 - AED 129.99)
- ✅ **All inventory set** (80 - 800 units)

**Total time:** ~10-15 minutes

**Next:** Start testing cart and checkout features! 🛒

---

## 🎯 Quick Tips

1. **Always authenticate first** - Make sure your JWT token is saved
2. **Check IDs** - After creating categories/brands, note their IDs
3. **Batch operations** - You can run multiple mutations in one request (like all 5 categories at once)
4. **Verify** - Use the "Get All Products" query to verify everything was created correctly

