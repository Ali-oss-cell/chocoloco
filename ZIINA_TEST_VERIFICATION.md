# 🧪 Ziina Payment Testing & Verification Guide

Complete guide to test and verify Ziina payments, orders, and inventory.

---

## 📋 Understanding the Flow

### Order Creation Timeline

```
STEP 1: Create Order (createRetailOrder)
├─ Order created with status: PENDING
├─ Inventory: RESERVED (not deducted)
├─ Cart: CLEARED
└─ Order Number: Generated (e.g., ORD-8B7FF47E)

STEP 2: Create Payment Session (createPaymentSession)
├─ Payment record created with status: PENDING
├─ Ziina payment URL generated
└─ Customer redirected to Ziina

STEP 3: Customer Pays on Ziina
├─ Customer enters test card
├─ Ziina processes payment
└─ Shows success page

STEP 4: Ziina Webhook (automatic)
├─ Ziina sends webhook to your backend
├─ Payment status updated: PENDING → COMPLETED
├─ Order status updated: PENDING → CONFIRMED
└─ Inventory: RESERVED → DEDUCTED

STEP 5: Order Fulfillment (admin manually)
├─ Admin updates: CONFIRMED → PROCESSING
├─ Admin updates: PROCESSING → SHIPPED
└─ Admin updates: SHIPPED → DELIVERED
```

---

## ✅ Step-by-Step Verification

### STEP 1: Check Order Was Created

After creating the order using `createRetailOrder`:

```graphql
query {
  orders(limit: 1) {
    id
    orderNumber
    status
    customerName
    customerEmail
    subtotal
    taxAmount
    deliveryFee
    totalAmount
    createdAt
    items {
      productName
      quantity
      unitPrice
      totalPrice
    }
    statusHistory {
      status
      notes
      createdAt
    }
  }
}
```

**Expected Results:**
- ✅ Order appears in the list
- ✅ Status: `PENDING`
- ✅ All items are listed
- ✅ Status history shows: "Order created"

---

### STEP 2: Check Inventory is Reserved

Query the product inventory:

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

**Expected Results:**
- ✅ `reservedQuantity` increased by order quantity
- ✅ `availableQuantity` decreased (but `quantityInStock` unchanged)
- Example: If you ordered 2 items:
  - Before: quantityInStock=100, reserved=0, available=100
  - After: quantityInStock=100, reserved=2, available=98

---

### STEP 3: Check Payment Record

Query the payment record:

```graphql
query {
  payments(limit: 1) {
    id
    paymentId
    order {
      orderNumber
    }
    gateway {
      name
    }
    status
    amount
    currency
    paymentMethod
    createdAt
    gatewayResponse
  }
}
```

**Expected Results:**
- ✅ Payment record exists
- ✅ Status: `PENDING` (before payment)
- ✅ Linked to correct order
- ✅ Gateway: Ziina
- ✅ Amount matches order total

---

### STEP 4: Test Ziina Payment (Test Mode)

Use Ziina test card:
- **Card Number:** `4242 4242 4242 4242`
- **Expiry:** Any future date (e.g., `12/25`)
- **CVV:** Any 3 digits (e.g., `123`)

**What Happens:**
1. You fill in the test card
2. Ziina shows success page
3. Ziina **should** send webhook to your backend

---

### STEP 5: Verify Payment Status Updated

After Ziina payment succeeds, check the payment status:

```graphql
query {
  payment(paymentId: "your-payment-id-here") {
    id
    paymentId
    status
    verifiedAt
    transactionId
    gatewayResponse
  }
}
```

**Expected Results:**
- ✅ Status: `COMPLETED` or `SUCCESS`
- ✅ `verifiedAt` has a timestamp
- ✅ `transactionId` populated

---

### STEP 6: Verify Order Status Updated

Check if order status was updated after payment:

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

**Expected Results:**
- ✅ Status: `CONFIRMED`
- ✅ `confirmedAt` has a timestamp
- ✅ Status history shows payment confirmation

---

### STEP 7: Verify Inventory Deducted

Check if inventory was properly deducted:

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

**Expected Results:**
- ✅ `quantityInStock` decreased by order quantity
- ✅ `reservedQuantity` decreased back to 0 (or previous value)
- Example: If you ordered 2 items:
  - Before payment: quantityInStock=100, reserved=2, available=98
  - After payment: quantityInStock=98, reserved=0, available=98

---

## 🚨 Common Issues & Solutions

### Issue 1: Order Created but Not in List

**Symptoms:**
- Order mutation returns success
- But `orders` query shows nothing

**Solutions:**
1. Make sure you're logged in as admin:
   ```graphql
   query {
     me {
       username
       isStaff
     }
   }
   ```

2. Check you're sending JWT token:
   ```
   Authorization: Bearer <your-token>
   ```

3. Query specific order by order number:
   ```graphql
   query {
     order(orderNumber: "ORD-8B7FF47E") {
       id
       orderNumber
     }
   }
   ```

---

### Issue 2: Payment Succeeds but Order Still PENDING

**Symptoms:**
- Ziina shows success page
- Payment status is PENDING
- Order status is PENDING

**Causes:**
- Webhook not received from Ziina
- Webhook URL not configured
- Webhook signature verification failed

**Solutions:**

1. **Check if webhook endpoint is accessible:**
   ```bash
   # Your webhook URL should be:
   https://your-domain.com/api/payments/webhooks/ziina/
   ```

2. **Test webhook manually:**
   ```graphql
   mutation {
     handleWebhook(
       payload: "{\"payment_id\": \"your-payment-id\", \"status\": \"completed\", \"amount\": \"119.98\"}"
       gatewayName: "ZIINA"
     ) {
       success
       message
       status
     }
   }
   ```

3. **Check Ziina dashboard:**
   - Log into Ziina merchant dashboard
   - Go to Webhooks section
   - Check if webhook was sent
   - Check webhook logs for errors

4. **Manually update order status:**
   ```graphql
   mutation {
     updateOrderStatus(input: {
       orderId: 1
       status: "CONFIRMED"
       notes: "Payment verified manually - Ziina payment ID: XXX"
     }) {
       success
       order {
         orderNumber
         status
       }
     }
   }
   ```

---

### Issue 3: Inventory Not Reserved

**Symptoms:**
- Order created
- But inventory numbers don't change

**Solutions:**

1. Check product has inventory set up:
   ```graphql
   query {
     product(id: 1) {
       name
       inventory {
         id
         quantityInStock
       }
     }
   }
   ```

2. If no inventory, create it:
   ```graphql
   mutation {
     updateInventory(input: {
       productId: 1
       quantityInStock: 100
       lowStockThreshold: 10
     }) {
       success
     }
   }
   ```

---

### Issue 4: Cannot View Orders (Not Authorized)

**Symptoms:**
```
"Not authorized"
```

**Solutions:**

1. Get admin JWT token first:
   ```graphql
   mutation {
     tokenAuth(username: "admin", password: "your-password") {
       token
       refreshToken
     }
   }
   ```

2. Add to Postman/Headers:
   ```
   Authorization: Bearer <token-from-above>
   ```

3. Verify you're staff:
   ```graphql
   query {
     me {
       username
       isStaff
       isSuperuser
     }
   }
   ```

---

## 🧪 Complete Test Scenario

### Test 1: Full Order Flow with Ziina

```graphql
# STEP 1: Add to cart
mutation {
  addToCart(
    sessionKey: "test-session-123"
    productId: 1
    quantity: 2
  ) {
    success
    cart {
      subtotal
      total
    }
  }
}

# STEP 2: Create order
mutation {
  createRetailOrder(
    sessionKey: "test-session-123"
    customerInfo: {
      name: "Test Customer"
      email: "test@example.com"
      phone: "+971501234567"
    }
    shippingAddress: {
      fullName: "Test Customer"
      phoneNumber: "+971501234567"
      email: "test@example.com"
      addressLine1: "123 Test Street"
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
      totalAmount
      status
    }
  }
}

# STEP 3: Check order in list (as admin)
query {
  orders(status: "PENDING") {
    orderNumber
    status
    totalAmount
    customerName
  }
}

# STEP 4: Check inventory reserved
query {
  product(id: 1) {
    inventory {
      quantityInStock
      reservedQuantity
      availableQuantity
    }
  }
}

# STEP 5: Create payment session
mutation {
  createPaymentSession(
    input: {
      orderId: "ORD-8B7FF47E"
      amount: "119.98"
      currency: "AED"
      customerEmail: "test@example.com"
      customerPhone: "+971501234567"
      customerName: "Test Customer"
      taxAmount: "5.00"
      shippingAmount: "15.00"
      items: [
        {
          name: "Test Product"
          price: "49.99"
          quantity: 2
          sku: "TEST-001"
        }
      ]
      shippingAddress: {
        fullName: "Test Customer"
        phoneNumber: "+971501234567"
        email: "test@example.com"
        addressLine1: "123 Test Street"
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
  }
}

# STEP 6: (Open paymentUrl in browser, pay with test card)
# Card: 4242 4242 4242 4242
# Expiry: 12/25
# CVV: 123

# STEP 7: After payment, verify payment status
query {
  payment(paymentId: "your-payment-id") {
    status
    verifiedAt
  }
}

# STEP 8: Verify order confirmed
query {
  order(orderNumber: "ORD-8B7FF47E") {
    status
    confirmedAt
    statusHistory {
      status
      notes
      createdAt
    }
  }
}

# STEP 9: Verify inventory deducted
query {
  product(id: 1) {
    inventory {
      quantityInStock
      reservedQuantity
      availableQuantity
    }
  }
}
```

---

## 📊 Checking Ziina Dashboard

To verify payment on Ziina's side:

1. **Login to Ziina Merchant Dashboard**
   - URL: https://merchant.ziina.com (or test dashboard)
   - Use your merchant credentials

2. **Go to Payments/Transactions**
   - Check if your test payment appears
   - Status should be "Completed" or "Successful"
   - Amount should match your order

3. **Check Webhook Logs**
   - Go to Developer → Webhooks
   - Check if webhook was sent to your backend
   - Check response status (should be 200)

---

## 🔧 Webhook Configuration

### Your Webhook URL

```
https://your-domain.com/api/payments/webhooks/ziina/
```

### In Ziina Dashboard

1. Go to Developer → Webhooks
2. Add webhook URL
3. Select events:
   - `payment.completed`
   - `payment.failed`
4. Save and test

### Test Webhook Locally (Development)

If testing locally, use ngrok:

```bash
# Start ngrok
ngrok http 8000

# Use the ngrok URL in Ziina dashboard
https://abc123.ngrok.io/api/payments/webhooks/ziina/
```

---

## 📝 Verification Checklist

After completing a test payment:

- [ ] Order appears in `orders` query
- [ ] Order status is `PENDING` initially
- [ ] Inventory is reserved (not deducted)
- [ ] Payment record created with status `PENDING`
- [ ] Payment URL generated and opens Ziina page
- [ ] Test card payment succeeds on Ziina
- [ ] Ziina shows success page
- [ ] Webhook received (check server logs)
- [ ] Payment status updated to `COMPLETED`
- [ ] Order status updated to `CONFIRMED`
- [ ] Order `confirmedAt` timestamp populated
- [ ] Inventory deducted from stock
- [ ] Reserved quantity decreased
- [ ] Status history shows payment confirmation
- [ ] Payment appears in Ziina dashboard

---

## 🎯 Quick Queries

**Get latest order:**
```graphql
query { orders(limit: 1) { orderNumber status totalAmount } }
```

**Get latest payment:**
```graphql
query { payments(limit: 1) { paymentId status amount } }
```

**Check inventory:**
```graphql
query { product(id: 1) { inventory { quantityInStock reservedQuantity availableQuantity } } }
```

**Get order with full details:**
```graphql
query {
  order(orderNumber: "ORD-XXX") {
    orderNumber
    status
    totalAmount
    confirmedAt
    items { productName quantity unitPrice }
    statusHistory { status notes createdAt }
  }
}
```

---

## 🚀 Summary

**What SHOULD happen automatically:**
1. ✅ Order created → Inventory reserved
2. ✅ Payment succeeds → Webhook sent
3. ✅ Webhook received → Order confirmed
4. ✅ Order confirmed → Inventory deducted

**What you MANUALLY do:**
1. Create cart & order
2. Pay on Ziina (test card)
3. Update order status (CONFIRMED → PROCESSING → SHIPPED → DELIVERED)

---

**You're all set to test!** 🎉

If webhooks aren't working in development, you can manually confirm orders using `updateOrderStatus` mutation.

