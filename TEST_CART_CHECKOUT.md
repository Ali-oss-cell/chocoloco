# 🛒 Test Cart & Checkout Flow

Complete customer shopping journey testing.

---

## 🛍️ STEP 1: Add Items to Cart

```graphql
mutation {
  # Add 3x Lindt Dark 85% (Product 1)
  item1: addToCart(
    sessionKey: "test-customer-001"
    productId: 1
    quantity: 3
  ) {
    success
    message
    cart {
      id
      sessionKey
      itemCount
      subtotal
      taxAmount
      total
      items {
        id
        product {
          name
          sku
        }
        quantity
        subtotal
      }
    }
  }
}
```

**Expected:**
- Cart created with 3 items
- Subtotal: AED 149.97 (3 × 49.99)
- Tax: AED 7.50 (5%)
- Total: AED 157.47

---

## 🛍️ STEP 2: Add More Items

```graphql
mutation {
  # Add 2x Lindt Lindor Milk Truffles (Product 9)
  item2: addToCart(
    sessionKey: "test-customer-001"
    productId: 9
    quantity: 2
  ) {
    success
    message
    cart {
      itemCount
      subtotal
      total
      items {
        product {
          name
        }
        quantity
        subtotal
      }
    }
  }
}
```

**Expected:**
- Now 5 items in cart (3 + 2)
- New subtotal: AED 269.95 (149.97 + 119.98)
- Total with tax: AED 283.45

---

## 🛍️ STEP 3: Add Gift Box

```graphql
mutation {
  # Add 1x Ferrero Rocher 16pc (Product 12)
  item3: addToCart(
    sessionKey: "test-customer-001"
    productId: 12
    quantity: 1
  ) {
    success
    message
    cart {
      itemCount
      subtotal
      total
    }
  }
}
```

**Expected:**
- Now 6 items total
- New subtotal: AED 349.94
- Total with tax: AED 367.44

---

## 🛒 STEP 4: View Full Cart

```graphql
query {
  cart(sessionKey: "test-customer-001") {
    id
    sessionKey
    itemCount
    subtotal
    taxAmount
    total
    createdAt
    updatedAt
    items {
      id
      product {
        id
        name
        sku
        brand {
          name
        }
        prices {
          salePrice
        }
        inventory {
          quantityInStock
        }
      }
      quantity
      subtotal
    }
  }
}
```

**Expected:** Complete cart details with all 3 products

---

## ✏️ STEP 5: Update Cart Item Quantity

**First, get the cart item ID from the cart (from Step 4 response):**

```graphql
mutation {
  updateCartItem(
    cartItemId: 1
    quantity: 5
  ) {
    success
    message
    cart {
      itemCount
      subtotal
      total
      items {
        id
        product {
          name
        }
        quantity
        subtotal
      }
    }
  }
}
```

**Expected:**
- Lindt Dark 85% updated from 3 to 5 pieces
- New subtotal and total recalculated

**Note:** Replace `cartItemId: 1` with the actual item ID from your cart query

---

## 🗑️ STEP 6: Remove Item from Cart

```graphql
mutation {
  removeFromCart(
    cartItemId: 2
  ) {
    success
    message
    cart {
      itemCount
      subtotal
      total
      items {
        id
        product {
          name
        }
        quantity
      }
    }
  }
}
```

**Expected:**
- Lindor truffles removed
- Only 2 products remaining in cart

**Note:** Replace `cartItemId: 2` with the actual item ID you want to remove

---

## 📦 STEP 7: Place Order (Checkout)

```graphql
mutation {
  createRetailOrder(
    sessionKey: "test-customer-001"
    customerInfo: {
      name: "Ahmed Al Maktoum"
      email: "ahmed@example.ae"
      phone: "+971501234567"
    }
    shippingAddress: {
      fullName: "Ahmed Al Maktoum"
      phoneNumber: "+971501234567"
      email: "ahmed@example.ae"
      addressLine1: "Villa 123, Palm Jumeirah"
      addressLine2: "Gate 5, Main Entrance"
      city: "Dubai"
      emirate: "DUBAI"
      postalCode: "12345"
      deliveryInstructions: "Please call before delivery"
    }
  ) {
    success
    message
    order {
      id
      orderNumber
      status
      subtotal
      taxAmount
      deliveryFee
      totalAmount
      currency
      customerName
      customerEmail
      customerPhone
      createdAt
      items {
        productName
        productSku
        quantity
        unitPrice
        taxAmount
        totalPrice
      }
      shippingAddress {
        fullName
        phoneNumber
        addressLine1
        city
        emirate
      }
      statusHistory {
        status
        notes
        createdAt
      }
    }
  }
}
```

**Expected:**
- Order created successfully
- Order number generated (e.g., ORD-2025100001)
- Status: PENDING
- Subtotal calculated
- Tax (VAT 5%) calculated
- Delivery fee added (based on emirate)
- Total amount = subtotal + tax + delivery
- Cart cleared automatically

---

## ✅ STEP 8: Verify Cart is Empty

```graphql
query {
  cart(sessionKey: "test-customer-001") {
    itemCount
    subtotal
    total
    items {
      id
    }
  }
}
```

**Expected:**
- Cart is empty (0 items)
- Subtotal: AED 0.00
- Total: AED 0.00

---

## 📋 STEP 9: View Order Details

```graphql
query {
  order(id: 1) {
    id
    orderNumber
    status
    totalAmount
    vat
    grandTotal
    paymentMethod
    paymentStatus
    customerEmail
    customerPhone
    notes
    createdAt
    items {
      product {
        name
        brand {
          name
        }
      }
      quantity
      priceAtOrder
      totalPrice
    }
    shippingAddress {
      fullName
      phoneNumber
      addressLine1
      addressLine2
      city
      emirate
      postalCode
    }
    statusHistory {
      status
      notes
      createdAt
    }
  }
}
```

**Expected:** Complete order details

---

## 🎯 Additional Tests

### Test 1: Add Item to New Cart

```graphql
mutation {
  addToCart(
    sessionKey: "test-customer-002"
    productId: 16
    quantity: 5
  ) {
    success
    cart {
      itemCount
      total
    }
  }
}
```

### Test 2: Multiple Items at Once

```graphql
mutation {
  item1: addToCart(sessionKey: "test-customer-003", productId: 1, quantity: 2) { success }
  item2: addToCart(sessionKey: "test-customer-003", productId: 2, quantity: 1) { success }
  item3: addToCart(sessionKey: "test-customer-003", productId: 3, quantity: 3) { success }
}
```

### Test 3: Clear Entire Cart

```graphql
mutation {
  clearCart(sessionKey: "test-customer-002") {
    success
    message
  }
}
```

---

## 🎉 Success Checklist

After completing all steps:

- ✅ Can add items to cart
- ✅ Can update quantities
- ✅ Can remove items
- ✅ Cart calculates totals correctly
- ✅ Can place order
- ✅ Order created with correct details
- ✅ Inventory deducted automatically
- ✅ Cart cleared after checkout
- ✅ Can view order details
- ✅ VAT calculated (5% UAE)

---

## 💡 What Happens Behind the Scenes

### When You Add to Cart:
1. ✅ Product exists and is active
2. ✅ Sufficient stock available
3. ✅ Cart item created/updated
4. ✅ Total calculated

### When You Checkout:
1. ✅ Validate all products in stock
2. ✅ Calculate VAT (5%)
3. ✅ Create order with PENDING status
4. ✅ Deduct inventory from stock
5. ✅ Create order items snapshot (price at order time)
6. ✅ Save shipping address
7. ✅ Create status history entry
8. ✅ Clear cart
9. ✅ Return order details

---

## 🚀 Real Customer Flow

```
Customer Journey:
1. Browse products → searchProducts("chocolate")
2. View product → product(id: 1)
3. Add to cart → addToCart(...)
4. Review cart → cart(sessionKey: "...")
5. Update quantities → updateCartItem(...)
6. Checkout → createRetailOrder(...)
7. Order confirmation → order(orderNumber: "...")
```

---

**Next:** Test order management (admin side)!  
See `TEST_ORDER_MANAGEMENT.md`

