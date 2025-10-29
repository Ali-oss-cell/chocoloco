# 📋 GraphQL Field Reference

Quick reference for all GraphQL field names in your schema.

---

## 🛒 Cart Fields

### CartType
```graphql
cart {
  id
  sessionKey          # Session identifier
  itemCount           # Total number of items
  subtotal            # Before tax
  taxAmount           # VAT 5%
  total               # Subtotal + tax
  createdAt
  updatedAt
  expiresAt
  items {
    # CartItemType fields...
  }
}
```

### CartItemType
```graphql
cartItem {
  id
  product {
    # ProductType fields...
  }
  quantity
  priceAtAddition     # Price when added to cart
  subtotal            # quantity × priceAtAddition
  productName         # Product name snapshot
  createdAt
  updatedAt
}
```

---

## 📦 Order Fields

### OrderType
```graphql
order {
  id
  orderNumber         # Unique order ID (e.g., ORD-2025100001)
  orderType           # RETAIL (WHOLESALE in Phase 2)
  status              # PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
  
  # Customer Info
  customerName
  customerEmail
  customerPhone
  customerCompany
  
  # Pricing
  subtotal            # Before tax and delivery
  discountAmount
  taxAmount           # VAT 5%
  deliveryFee         # Based on emirate
  totalAmount         # subtotal + tax + delivery - discount
  currency            # AED
  
  # Timestamps
  createdAt
  updatedAt
  confirmedAt
  deliveredAt
  cancelledAt
  
  # Relations
  items {
    # OrderItemType fields...
  }
  shippingAddress {
    # ShippingAddressType fields...
  }
  statusHistory {
    # OrderStatusHistoryType fields...
  }
  
  notes
}
```

### OrderItemType
```graphql
orderItem {
  id
  product {
    # ProductType (reference)
  }
  productName         # Snapshot at time of order
  productSku          # Snapshot at time of order
  quantity
  unitPrice           # Price per unit at time of order
  discountAmount
  taxAmount           # Item tax
  totalPrice          # (unitPrice × quantity) - discount + tax
  createdAt
}
```

### ShippingAddressType
```graphql
shippingAddress {
  id
  fullName
  phoneNumber
  email
  addressLine1
  addressLine2
  city
  emirate             # DUBAI, ABU_DHABI, SHARJAH, etc.
  area
  postalCode
  deliveryInstructions
  latitude
  longitude
  createdAt
}
```

### OrderStatusHistoryType
```graphql
statusHistory {
  id
  status              # Status at this point
  notes               # Change description
  createdAt           # When status changed
}
```

---

## 🍫 Product Fields

### ProductType
```graphql
product {
  id
  sku
  name
  slug
  brand {
    # BrandType fields...
  }
  category {
    # CategoryType fields...
  }
  description
  shortDescription
  ingredients
  allergenInfo
  weight
  volume
  unitType            # PIECE, GRAM, KG, ML, L, BOX
  isActive
  featured
  createdAt
  updatedAt
  
  # Relations
  prices {
    # ProductPriceType fields...
  }
  inventory {
    # InventoryType fields...
  }
  images {
    # ProductImageType fields...
  }
  reviews {
    # ProductReviewType fields...
  }
}
```

### ProductPriceType
```graphql
price {
  id
  priceType           # RETAIL or WHOLESALE
  basePrice
  salePrice
  minQuantity
  maxQuantity
  isActive
  validFrom
  validUntil
  createdAt
  updatedAt
}
```

### InventoryType
```graphql
inventory {
  id
  quantityInStock
  reservedQuantity
  availableQuantity   # quantityInStock - reservedQuantity
  lowStockThreshold
  isInStock           # availableQuantity > 0
  warehouseLocation
  lastRestocked
  updatedAt
}
```

### CategoryType
```graphql
category {
  id
  name
  slug
  description
  parentCategory {
    # CategoryType (recursive)
  }
  isActive
  displayOrder
  createdAt
  updatedAt
}
```

### BrandType
```graphql
brand {
  id
  name
  slug
  description
  logo
  countryOfOrigin
  isActive
  displayOrder
  createdAt
  updatedAt
}
```

---

## 🔍 Common Mistakes

### ❌ Wrong → ✅ Correct

| Wrong | Correct |
|-------|---------|
| `sessionId` | `sessionKey` |
| `totalItems` | `itemCount` |
| `totalPrice` | `total` or `totalAmount` |
| `vat` | `taxAmount` |
| `grandTotal` | `totalAmount` |
| `priceAtOrder` | `unitPrice` |
| `priceAtTime` | `priceAtAddition` or `subtotal` |
| `paymentMethod` | (not implemented yet) |

---

## 🎯 Mutation Arguments

### Cart Mutations

```graphql
# Add to cart
addToCart(
  sessionKey: String!
  productId: Int!
  quantity: Int!
)

# Update cart item
updateCartItem(
  cartItemId: Int!    # ← Use cart item ID, not product ID
  quantity: Int!
)

# Remove from cart
removeFromCart(
  cartItemId: Int!    # ← Use cart item ID, not product ID
)

# Clear cart
clearCart(
  sessionKey: String!
)
```

### Order Mutations

```graphql
# Create retail order
createRetailOrder(
  sessionKey: String!
  customerInfo: CustomerInput!
  shippingAddress: AddressInput!
)

# Update order status (admin)
updateOrderStatus(
  input: UpdateOrderStatusInput!
)

# Cancel order (admin)
cancelOrder(
  orderId: Int!
  reason: String
)

# Update shipping address (admin)
updateShippingAddress(
  orderId: Int!
  fullName: String
  phoneNumber: String
  addressLine1: String
  # ... other address fields
)
```

### Product Admin Mutations

```graphql
# Create product
createProduct(
  input: ProductInput!
)

# Set price
setProductPrice(
  input: ProductPriceInput!
)

# Update inventory
updateInventory(
  input: InventoryInput!
)
```

---

## 📊 Input Types

### CustomerInput
```graphql
{
  name: String!
  email: String!
  phone: String!
  company: String
}
```

### AddressInput
```graphql
{
  fullName: String!
  phoneNumber: String!
  email: String!
  addressLine1: String!
  addressLine2: String
  city: String!
  emirate: String!      # DUBAI, ABU_DHABI, etc.
  area: String
  postalCode: String
  deliveryInstructions: String
}
```

### ProductInput
```graphql
{
  sku: String
  name: String!
  slug: String
  brandId: Int!
  categoryId: Int!
  description: String
  shortDescription: String
  ingredients: String
  allergenInfo: String
  weight: Decimal       # Use quotes: "100.0"
  volume: Decimal       # Use quotes: "500.0"
  unitType: String
  isActive: Boolean
  featured: Boolean
}
```

### ProductPriceInput
```graphql
{
  productId: Int!
  priceType: String!    # "RETAIL" or "WHOLESALE"
  basePrice: Decimal!   # Use quotes: "45.00"
  salePrice: Decimal    # Use quotes: "39.99"
  minQuantity: Int
  isActive: Boolean
}
```

### InventoryInput
```graphql
{
  productId: Int!
  quantityInStock: Int!
  lowStockThreshold: Int
  warehouseLocation: String
}
```

---

## 💡 Tips

1. **Decimal fields** require quotes: `"45.00"` not `45.00`
2. **Emirates** must be uppercase: `"DUBAI"` not `"Dubai"`
3. **Cart item operations** use `cartItemId`, not `productId`
4. **Order queries** use `orderNumber` (string), not `id` (int)
5. **Always check** `success` field in mutation responses

---

## 🔗 Quick Links

- Full mutation examples: `ADMIN_API_GUIDE.md`
- Cart testing: `QUICK_CART_TEST.md`
- Complete testing: `COMPLETE_TESTING_GUIDE.md`
- Schema overview: `SCHEMA_SUMMARY.md`

---

**Keep this file open while testing!** 📌

