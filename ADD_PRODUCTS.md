# 🍫 Add 20 Real Products - Complete Workflow

Copy and paste these mutations into GraphiQL: `http://localhost:8000/graphql/`

---

## 📦 STEP 1: Create Categories (5 categories)

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

**Expected:** 5 categories created (IDs 1-5)

---

## 🏭 STEP 2: Create Brands (5 brands)

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

**Expected:** 5 brands created (IDs 1-5)

---

## 🍫 STEP 3: Create 20 Products

### Batch 1: Products 1-5 (Lindt Dark Chocolates)

```graphql
mutation {
  p1: createProduct(input: {
    sku: "LINDT-DARK-85"
    name: "Lindt Excellence Dark 85%"
    slug: "lindt-excellence-dark-85"
    brandId: 1
    categoryId: 1
    description: "Intense dark chocolate with 85% cocoa content"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p2: createProduct(input: {
    sku: "LINDT-DARK-70"
    name: "Lindt Excellence Dark 70%"
    slug: "lindt-excellence-dark-70"
    brandId: 1
    categoryId: 1
    description: "Smooth dark chocolate with 70% cocoa"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p3: createProduct(input: {
    sku: "LINDT-SEA-SALT"
    name: "Lindt Dark Sea Salt"
    slug: "lindt-dark-sea-salt"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate with a touch of sea salt"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
  
  p4: createProduct(input: {
    sku: "LINDT-ORANGE"
    name: "Lindt Dark Orange Intense"
    slug: "lindt-dark-orange"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate with natural orange flavor"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
  
  p5: createProduct(input: {
    sku: "LINDT-MINT"
    name: "Lindt Dark Mint Intense"
    slug: "lindt-dark-mint"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate with refreshing mint"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
}
```

### Batch 2: Products 6-10 (Lindt Milk & White)

```graphql
mutation {
  p6: createProduct(input: {
    sku: "LINDT-MILK-001"
    name: "Lindt Milk Chocolate Classic"
    slug: "lindt-milk-classic"
    brandId: 1
    categoryId: 2
    description: "Smooth and creamy milk chocolate"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p7: createProduct(input: {
    sku: "LINDT-MILK-HAZEL"
    name: "Lindt Milk Chocolate with Hazelnuts"
    slug: "lindt-milk-hazelnut"
    brandId: 1
    categoryId: 2
    description: "Creamy milk chocolate with whole hazelnuts"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
  
  p8: createProduct(input: {
    sku: "LINDT-WHITE-001"
    name: "Lindt White Chocolate"
    slug: "lindt-white-chocolate"
    brandId: 1
    categoryId: 3
    description: "Delicate white chocolate"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
  
  p9: createProduct(input: {
    sku: "LINDT-LINDOR-MILK"
    name: "Lindt Lindor Milk Chocolate Truffles"
    slug: "lindt-lindor-milk"
    brandId: 1
    categoryId: 2
    description: "Irresistibly smooth melting truffles"
    weight: "200.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p10: createProduct(input: {
    sku: "LINDT-LINDOR-DARK"
    name: "Lindt Lindor Dark Chocolate Truffles"
    slug: "lindt-lindor-dark"
    brandId: 1
    categoryId: 1
    description: "Dark chocolate truffles with smooth filling"
    weight: "200.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
}
```

### Batch 3: Products 11-15 (Other Brands)

```graphql
mutation {
  p11: createProduct(input: {
    sku: "GODIVA-DARK-001"
    name: "Godiva Dark Chocolate Bar 72%"
    slug: "godiva-dark-72"
    brandId: 2
    categoryId: 1
    description: "Belgian dark chocolate masterpiece"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p12: createProduct(input: {
    sku: "FERRERO-BOX-16"
    name: "Ferrero Rocher Collection 16 pieces"
    slug: "ferrero-rocher-16"
    brandId: 3
    categoryId: 5
    description: "Luxury hazelnut chocolates in gold foil"
    weight: "200.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p13: createProduct(input: {
    sku: "TOBLERONE-MILK-100"
    name: "Toblerone Milk Chocolate"
    slug: "toblerone-milk-100"
    brandId: 4
    categoryId: 4
    description: "Swiss milk chocolate with honey and almond nougat"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
  
  p14: createProduct(input: {
    sku: "TOBLERONE-DARK-100"
    name: "Toblerone Dark Chocolate"
    slug: "toblerone-dark-100"
    brandId: 4
    categoryId: 4
    description: "Swiss dark chocolate with honey and almond"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
  
  p15: createProduct(input: {
    sku: "TOBLERONE-WHITE-100"
    name: "Toblerone White Chocolate"
    slug: "toblerone-white-100"
    brandId: 4
    categoryId: 4
    description: "White chocolate with honey and almond nougat"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
  }) { success product { id } }
}
```

### Batch 4: Products 16-20 (More Variety)

```graphql
mutation {
  p16: createProduct(input: {
    sku: "CADBURY-DAIRY-MILK"
    name: "Cadbury Dairy Milk Chocolate"
    slug: "cadbury-dairy-milk"
    brandId: 5
    categoryId: 2
    description: "Classic British milk chocolate"
    weight: "100.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p17: createProduct(input: {
    sku: "GODIVA-GIFT-BOX"
    name: "Godiva Chocolate Gift Box Assortment"
    slug: "godiva-gift-box"
    brandId: 2
    categoryId: 5
    description: "Premium Belgian chocolate assortment"
    weight: "250.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p18: createProduct(input: {
    sku: "LINDT-SWISS-LUXURY"
    name: "Lindt Swiss Luxury Selection"
    slug: "lindt-swiss-luxury"
    brandId: 1
    categoryId: 5
    description: "Assorted Swiss chocolates in premium box"
    weight: "230.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p19: createProduct(input: {
    sku: "FERRERO-BOX-24"
    name: "Ferrero Rocher Collection 24 pieces"
    slug: "ferrero-rocher-24"
    brandId: 3
    categoryId: 5
    description: "Large luxury hazelnut chocolate gift box"
    weight: "300.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
  
  p20: createProduct(input: {
    sku: "GODIVA-TRUFFLE-ASST"
    name: "Godiva Signature Chocolate Truffles"
    slug: "godiva-truffle-assortment"
    brandId: 2
    categoryId: 5
    description: "Handcrafted Belgian chocolate truffles"
    weight: "180.0"
    unitType: "GRAM"
    isActive: true
    featured: true
  }) { success product { id } }
}
```

**Expected:** 20 products created (IDs 1-20)

---

## 💰 STEP 4: Set Prices for All Products

```graphql
mutation {
  # Products 1-5: Lindt Dark (AED 45-55)
  pr1: setProductPrice(input: {productId: 1, priceType: "RETAIL", basePrice: "55.00", salePrice: "49.99", minQuantity: 1, isActive: true}) { success }
  pr2: setProductPrice(input: {productId: 2, priceType: "RETAIL", basePrice: "50.00", salePrice: "44.99", minQuantity: 1, isActive: true}) { success }
  pr3: setProductPrice(input: {productId: 3, priceType: "RETAIL", basePrice: "52.00", salePrice: "46.99", minQuantity: 1, isActive: true}) { success }
  pr4: setProductPrice(input: {productId: 4, priceType: "RETAIL", basePrice: "48.00", minQuantity: 1, isActive: true}) { success }
  pr5: setProductPrice(input: {productId: 5, priceType: "RETAIL", basePrice: "48.00", minQuantity: 1, isActive: true}) { success }
  
  # Products 6-10: Lindt Milk/White (AED 35-65)
  pr6: setProductPrice(input: {productId: 6, priceType: "RETAIL", basePrice: "42.00", salePrice: "37.99", minQuantity: 1, isActive: true}) { success }
  pr7: setProductPrice(input: {productId: 7, priceType: "RETAIL", basePrice: "45.00", minQuantity: 1, isActive: true}) { success }
  pr8: setProductPrice(input: {productId: 8, priceType: "RETAIL", basePrice: "40.00", minQuantity: 1, isActive: true}) { success }
  pr9: setProductPrice(input: {productId: 9, priceType: "RETAIL", basePrice: "68.00", salePrice: "59.99", minQuantity: 1, isActive: true}) { success }
  pr10: setProductPrice(input: {productId: 10, priceType: "RETAIL", basePrice: "65.00", minQuantity: 1, isActive: true}) { success }
  
  # Products 11-15: Other brands (AED 45-85)
  pr11: setProductPrice(input: {productId: 11, priceType: "RETAIL", basePrice: "75.00", salePrice: "69.99", minQuantity: 1, isActive: true}) { success }
  pr12: setProductPrice(input: {productId: 12, priceType: "RETAIL", basePrice: "85.00", salePrice: "79.99", minQuantity: 1, isActive: true}) { success }
  pr13: setProductPrice(input: {productId: 13, priceType: "RETAIL", basePrice: "38.00", minQuantity: 1, isActive: true}) { success }
  pr14: setProductPrice(input: {productId: 14, priceType: "RETAIL", basePrice: "40.00", minQuantity: 1, isActive: true}) { success }
  pr15: setProductPrice(input: {productId: 15, priceType: "RETAIL", basePrice: "38.00", minQuantity: 1, isActive: true}) { success }
  
  # Products 16-20: More variety (AED 35-120)
  pr16: setProductPrice(input: {productId: 16, priceType: "RETAIL", basePrice: "35.00", salePrice: "29.99", minQuantity: 1, isActive: true}) { success }
  pr17: setProductPrice(input: {productId: 17, priceType: "RETAIL", basePrice: "125.00", salePrice: "109.99", minQuantity: 1, isActive: true}) { success }
  pr18: setProductPrice(input: {productId: 18, priceType: "RETAIL", basePrice: "95.00", salePrice: "84.99", minQuantity: 1, isActive: true}) { success }
  pr19: setProductPrice(input: {productId: 19, priceType: "RETAIL", basePrice: "145.00", salePrice: "129.99", minQuantity: 1, isActive: true}) { success }
  pr20: setProductPrice(input: {productId: 20, priceType: "RETAIL", basePrice: "88.00", salePrice: "79.99", minQuantity: 1, isActive: true}) { success }
}
```

**Expected:** All 20 products now have prices

---

## 📦 STEP 5: Set Inventory for All Products

```graphql
mutation {
  inv1: updateInventory(input: {productId: 1, quantityInStock: 500, lowStockThreshold: 50}) { success }
  inv2: updateInventory(input: {productId: 2, quantityInStock: 450, lowStockThreshold: 50}) { success }
  inv3: updateInventory(input: {productId: 3, quantityInStock: 300, lowStockThreshold: 30}) { success }
  inv4: updateInventory(input: {productId: 4, quantityInStock: 250, lowStockThreshold: 30}) { success }
  inv5: updateInventory(input: {productId: 5, quantityInStock: 250, lowStockThreshold: 30}) { success }
  inv6: updateInventory(input: {productId: 6, quantityInStock: 600, lowStockThreshold: 60}) { success }
  inv7: updateInventory(input: {productId: 7, quantityInStock: 400, lowStockThreshold: 40}) { success }
  inv8: updateInventory(input: {productId: 8, quantityInStock: 350, lowStockThreshold: 35}) { success }
  inv9: updateInventory(input: {productId: 9, quantityInStock: 200, lowStockThreshold: 25}) { success }
  inv10: updateInventory(input: {productId: 10, quantityInStock: 180, lowStockThreshold: 25}) { success }
  inv11: updateInventory(input: {productId: 11, quantityInStock: 300, lowStockThreshold: 30}) { success }
  inv12: updateInventory(input: {productId: 12, quantityInStock: 150, lowStockThreshold: 20}) { success }
  inv13: updateInventory(input: {productId: 13, quantityInStock: 400, lowStockThreshold: 40}) { success }
  inv14: updateInventory(input: {productId: 14, quantityInStock: 350, lowStockThreshold: 35}) { success }
  inv15: updateInventory(input: {productId: 15, quantityInStock: 300, lowStockThreshold: 30}) { success }
  inv16: updateInventory(input: {productId: 16, quantityInStock: 800, lowStockThreshold: 80}) { success }
  inv17: updateInventory(input: {productId: 17, quantityInStock: 100, lowStockThreshold: 15}) { success }
  inv18: updateInventory(input: {productId: 18, quantityInStock: 120, lowStockThreshold: 15}) { success }
  inv19: updateInventory(input: {productId: 19, quantityInStock: 80, lowStockThreshold: 10}) { success }
  inv20: updateInventory(input: {productId: 20, quantityInStock: 90, lowStockThreshold: 12}) { success }
}
```

**Expected:** All 20 products now have inventory

---

## ✅ STEP 6: Verify All Products

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
      isInStock
    }
  }
}
```

**Expected:** See all 20 products with complete data!

---

## 🎉 Success!

You now have:
- ✅ 5 Categories
- ✅ 5 Brands
- ✅ 20 Products
- ✅ All prices set (AED 29.99 - AED 129.99)
- ✅ All inventory set (80 - 800 units)

**Next:** Test cart and checkout! See `TEST_CART_CHECKOUT.md`

