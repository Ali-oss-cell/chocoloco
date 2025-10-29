# 🛒 Quick Cart Test - Fixed Version

Use these corrected mutations to test the cart system.

---

## ✅ STEP 1: Add Item to Cart

```graphql
mutation {
  addToCart(
    sessionKey: "test-123"
    productId: 1
    quantity: 2
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
        }
        quantity
        subtotal
      }
    }
  }
}
```

---

## ✅ STEP 2: View Cart

```graphql
query {
  cart(sessionKey: "test-123") {
    sessionKey
    itemCount
    subtotal
    taxAmount
    total
    items {
      id
      product {
        id
        name
        sku
      }
      quantity
      subtotal
    }
  }
}
```

---

## ✅ STEP 3: Update Cart Item

**Use the cart item ID from Step 2 response:**

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
      total
    }
  }
}
```

---

## ✅ STEP 4: Add Another Product

```graphql
mutation {
  addToCart(
    sessionKey: "test-123"
    productId: 2
    quantity: 1
  ) {
    success
    cart {
      itemCount
      total
    }
  }
}
```

---

## ✅ STEP 5: Checkout (Create Order)

```graphql
mutation {
  createRetailOrder(
    sessionKey: "test-123"
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
      city: "Dubai"
      emirate: "DUBAI"
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
        city
        emirate
      }
    }
  }
}
```

---

## 🎯 Key Points

### Field Names (Corrected):
- ✅ `sessionKey` (not `sessionId`)
- ✅ `itemCount` (not `totalItems`)
- ✅ `total`, `subtotal`, `taxAmount` (not `totalPrice`)
- ✅ `cartItemId` for update/remove (not `productId`)

### Input Structure:
- `addToCart`: `sessionKey`, `productId`, `quantity`
- `updateCartItem`: `cartItemId`, `quantity`
- `removeFromCart`: `cartItemId`
- `createRetailOrder`: `sessionKey`, `customerInfo`, `shippingAddress`

### Emirates (Uppercase):
- DUBAI
- ABU_DHABI  
- SHARJAH
- AJMAN
- UMM_AL_QUWAIN
- RAS_AL_KHAIMAH
- FUJAIRAH

---

**Try STEP 1 now!** 🚀

