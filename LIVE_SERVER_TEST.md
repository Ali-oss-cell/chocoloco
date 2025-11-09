# 🚀 Live Server Testing Guide

Complete step-by-step test on your live server: **http://164.90.215.173/graphql/**

---

## 🔐 STEP 1: Login as Admin

**URL:** `http://164.90.215.173/graphql/`

**GraphQL Mutation:**
```graphql
mutation {
  tokenAuth(username: "admin", password: "your-admin-password") {
    token
    refreshToken
    user {
      username
      email
      isStaff
      isSuperuser
    }
  }
}
```

**Save the token!** You'll need it for all admin operations.

---

## 📦 STEP 2: Check Products

**GraphQL Query:**
```graphql
query {
  products(limit: 5) {
    id
    name
    sku
    slug
    isActive
    prices {
      basePrice
      salePrice
      priceType
    }
    inventory {
      id
      quantityInStock
      reservedQuantity
      availableQuantity
      isInStock
    }
    images {
      image
      isPrimary
    }
  }
}
```

**Expected:** List of products with inventory

**Note:** Pick a product ID for testing (e.g., `id: 1`)

---

## 🛒 STEP 3: Add to Cart (No Auth Required)

**GraphQL Mutation:**
```graphql
mutation {
  addToCart(
    sessionKey: "live-test-session-123"
    productId: 1
    quantity: 2
  ) {
    success
    message
    cartItem {
      id
      quantity
      priceAtAddition
    }
    cart {
      id
      sessionKey
      subtotal
      taxAmount
      total
      itemCount
    }
  }
}
```

**Expected:**
- ✅ Success: true
- ✅ Cart total calculated
- ✅ Message: "Added to cart..."

**Important:** Save the `sessionKey` value!

---

## 🛒 STEP 4: View Cart

**GraphQL Query:**
```graphql
query {
  cart(sessionKey: "live-test-session-123") {
    id
    sessionKey
    subtotal
    taxAmount
    total
    itemCount
    items {
      id
      quantity
      priceAtAddition
      subtotal
      product {
        name
        sku
      }
    }
  }
}
```

**Expected:** Cart with items and totals

---

## 📝 STEP 5: Create Order

**GraphQL Mutation:**
```graphql
mutation {
  createRetailOrder(
    sessionKey: "live-test-session-123"
    customerInfo: {
      name: "Ahmed Al Maktoum"
      email: "ahmed@test.ae"
      phone: "+971501234567"
    }
    shippingAddress: {
      fullName: "Ahmed Al Maktoum"
      phoneNumber: "+971501234567"
      email: "ahmed@test.ae"
      addressLine1: "Villa 123, Palm Jumeirah"
      city: "Dubai"
      emirate: "DUBAI"
      postalCode: "12345"
    }
  ) {
    success
    message
    order {
      id
      orderNumber
      status
      orderType
      customerName
      customerEmail
      subtotal
      taxAmount
      deliveryFee
      totalAmount
      items {
        productName
        quantity
        unitPrice
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

**Expected:**
- ✅ Success: true
- ✅ Order number generated (e.g., ORD-8B7FF47E)
- ✅ Status: PENDING
- ✅ Total amount calculated

**SAVE THE ORDER NUMBER AND ORDER ID!**

---

## 👁️ STEP 6: View Order (Admin Only)

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Query:**
```graphql
query {
  order(orderNumber: "ORD-8B7FF47E") {
    id
    orderNumber
    status
    orderType
    customerName
    customerEmail
    customerPhone
    subtotal
    taxAmount
    deliveryFee
    totalAmount
    createdAt
    items {
      id
      productName
      productSku
      quantity
      unitPrice
      totalPrice
    }
    shippingAddress {
      fullName
      phoneNumber
      addressLine1
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

**Expected:**
- ✅ Full order details
- ✅ Status: PENDING
- ✅ Status history: "Order created"

---

## 📋 STEP 7: View All Orders (Admin Only)

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Query:**
```graphql
query {
  orders(limit: 10) {
    id
    orderNumber
    status
    customerName
    customerEmail
    totalAmount
    createdAt
    items {
      productName
      quantity
    }
  }
}
```

**Expected:** List of all orders including your test order

---

## 📊 STEP 8: Check Inventory Reserved

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Query:**
```graphql
query {
  product(id: 1) {
    id
    name
    inventory {
      quantityInStock
      reservedQuantity
      availableQuantity
      isInStock
    }
  }
}
```

**Expected:**
- ✅ `reservedQuantity` increased by order quantity
- ✅ `availableQuantity` decreased
- ✅ `quantityInStock` unchanged (will be deducted after payment)

---

## 💳 STEP 9: Create Payment Session (Ziina)

**GraphQL Mutation:**
```graphql
mutation {
  createPaymentSession(
    input: {
      orderId: "ORD-8B7FF47E"
      amount: "119.98"
      currency: "AED"
      customerEmail: "ahmed@test.ae"
      customerPhone: "+971501234567"
      customerName: "Ahmed Al Maktoum"
      taxAmount: "5.00"
      shippingAmount: "15.00"
      discountAmount: "0.00"
      items: [
        {
          name: "Test Product"
          price: "49.99"
          quantity: 2
          sku: "TEST-001"
        }
      ]
      shippingAddress: {
        fullName: "Ahmed Al Maktoum"
        phoneNumber: "+971501234567"
        email: "ahmed@test.ae"
        addressLine1: "Villa 123, Palm Jumeirah"
        city: "Dubai"
        emirate: "DUBAI"
        postalCode: "12345"
      }
    }
    gatewayName: "ZIINA"
  ) {
    success
    message
    paymentUrl
    paymentId
    expiresAt
    gatewayResponse
  }
}
```

**Expected:**
- ✅ Success: true
- ✅ `paymentUrl` generated
- ✅ `paymentId` created

**SAVE THE PAYMENT URL AND PAYMENT ID!**

---

## 💰 STEP 10: Pay on Ziina (Test Card)

1. **Open the `paymentUrl` in your browser**
   - Example: `https://pay.ziina.com/payment/xxx`

2. **Use Ziina Test Card:**
   - Card Number: `4242 4242 4242 4242`
   - Expiry: `12/25` (any future date)
   - CVV: `123` (any 3 digits)
   - Name: Any name

3. **Complete Payment**
   - Click "Pay Now"
   - Should see success page

---

## ✅ STEP 11: Verify Payment Status

**GraphQL Query:**
```graphql
query {
  payment(paymentId: "your-payment-id-here") {
    id
    paymentId
    order {
      orderNumber
      status
    }
    gateway {
      name
    }
    status
    amount
    currency
    paymentMethod
    verifiedAt
    transactionId
    createdAt
    gatewayResponse
  }
}
```

**Expected:**
- Status should be `COMPLETED` or `SUCCESS` (if webhook worked)
- Or still `PENDING` (if webhook didn't work yet)

---

## 📦 STEP 12: Check Order Status Updated

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Query:**
```graphql
query {
  order(orderNumber: "ORD-8B7FF47E") {
    orderNumber
    status
    confirmedAt
    statusHistory {
      status
      notes
      createdAt
    }
  }
}
```

**Expected (if webhook worked):**
- ✅ Status: `CONFIRMED`
- ✅ `confirmedAt` has timestamp
- ✅ Status history shows payment confirmation

**If status still PENDING:**
- Webhook didn't arrive yet
- See Step 13 to manually confirm

---

## 📊 STEP 13: Check Inventory Deducted

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Query:**
```graphql
query {
  product(id: 1) {
    name
    inventory {
      quantityInStock
      reservedQuantity
      availableQuantity
    }
  }
}
```

**Expected (if payment confirmed):**
- ✅ `quantityInStock` decreased
- ✅ `reservedQuantity` back to 0
- ✅ `availableQuantity` decreased

---

## 🔧 STEP 14: Manual Confirmation (If Webhook Didn't Work)

If order is still PENDING after payment:

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Mutation:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "Payment verified manually - Ziina test payment successful"
  }) {
    success
    message
    order {
      orderNumber
      status
      confirmedAt
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
- ✅ Status updated to CONFIRMED
- ✅ Status history updated
- ✅ Inventory deducted

---

## 🚚 STEP 15: Update Order to Processing

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Mutation:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "PROCESSING"
    notes: "Order being prepared in warehouse"
  }) {
    success
    message
    order {
      orderNumber
      status
    }
  }
}
```

---

## 📦 STEP 16: Update Order to Shipped

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Mutation:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "SHIPPED"
    notes: "Shipped via Aramex - Tracking: AE123456789"
  }) {
    success
    message
    order {
      orderNumber
      status
    }
  }
}
```

---

## ✅ STEP 17: Update Order to Delivered

**Headers Required:**
```
Authorization: Bearer <your-token-from-step-1>
```

**GraphQL Mutation:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "DELIVERED"
    notes: "Delivered successfully - Signature received"
  }) {
    success
    message
    order {
      orderNumber
      status
      deliveredAt
      statusHistory {
        status
        notes
        createdAt
      }
    }
  }
}
```

---

## 🧪 BONUS: Test Order Cancellation

Create a new test order and cancel it:

**Step 1: Create New Order**
```graphql
mutation {
  addToCart(sessionKey: "cancel-test-123", productId: 1, quantity: 1) {
    success
  }
}

mutation {
  createRetailOrder(
    sessionKey: "cancel-test-123"
    customerInfo: {
      name: "Cancel Test"
      email: "cancel@test.ae"
      phone: "+971509999999"
    }
    shippingAddress: {
      fullName: "Cancel Test"
      phoneNumber: "+971509999999"
      email: "cancel@test.ae"
      addressLine1: "Test Address"
      city: "Dubai"
      emirate: "DUBAI"
    }
  ) {
    success
    order {
      id
      orderNumber
    }
  }
}
```

**Step 2: Cancel Order**

**Headers Required:**
```
Authorization: Bearer <your-token>
```

```graphql
mutation {
  cancelOrder(
    orderId: 2
    reason: "Customer requested cancellation - Testing"
  ) {
    success
    message
    order {
      orderNumber
      status
      statusHistory {
        status
        notes
      }
    }
  }
}
```

**Expected:**
- ✅ Order status: CANCELLED
- ✅ Inventory returned to stock automatically

---

## 📝 Testing Checklist

After completing all steps:

- [ ] ✅ Admin login works
- [ ] ✅ Can view products
- [ ] ✅ Can add to cart (no auth)
- [ ] ✅ Can create order
- [ ] ✅ Order appears in orders list (admin)
- [ ] ✅ Inventory reserved on order creation
- [ ] ✅ Payment session created
- [ ] ✅ Payment URL opens Ziina page
- [ ] ✅ Test card payment succeeds
- [ ] ✅ Payment status updated
- [ ] ✅ Order status updated to CONFIRMED
- [ ] ✅ Inventory deducted after payment
- [ ] ✅ Can update order status (admin)
- [ ] ✅ Can cancel order (admin)
- [ ] ✅ Inventory restored on cancellation

---

## 🔧 Webhook Configuration for Live Server

To make webhooks work automatically:

**Your webhook URL:**
```
http://164.90.215.173/api/payments/webhooks/ziina/
```

**Configure in Ziina Dashboard:**
1. Login to Ziina merchant dashboard
2. Go to Developer → Webhooks
3. Add webhook URL: `http://164.90.215.173/api/payments/webhooks/ziina/`
4. Select events: `payment.completed`, `payment.failed`
5. Save

**Test webhook endpoint:**
```bash
curl -X POST http://164.90.215.173/api/payments/webhooks/ziina/ \
  -H "Content-Type: application/json" \
  -d '{"payment_id":"test","status":"completed","amount":"100.00"}'
```

---

## 🚨 Troubleshooting

### Error: "Not authorized"
**Solution:** Make sure you include the JWT token in headers:
```
Authorization: Bearer <your-token>
```

### Error: "Product not found"
**Solution:** Use a valid product ID from the products query in Step 2.

### Error: "Cart not found"
**Solution:** Make sure you use the same `sessionKey` for cart and order operations.

### Payment succeeds but order still PENDING
**Solution:** 
1. Check if webhook URL is configured in Ziina dashboard
2. Manually confirm order using `updateOrderStatus` mutation (Step 14)

### Cannot see orders
**Solution:** Make sure your user has `is_staff=True`

---

## 🎯 Quick Reference

**Server URL:** `http://164.90.215.173/graphql/`

**Auth Header:**
```
Authorization: Bearer <token>
```

**Test Card:**
- Card: `4242 4242 4242 4242`
- Expiry: `12/25`
- CVV: `123`

**Webhook URL:**
```
http://164.90.215.173/api/payments/webhooks/ziina/
```

---

**Ready to test!** 🚀

Follow the steps in order. If you get stuck on any step, let me know which step and what error you're seeing.

