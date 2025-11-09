# 💳 Complete Payment Flow Guide

Step-by-step guide for the complete payment process from cart to order completion.

---

## 📋 Complete Flow Overview

```
1. User adds items to cart
   ↓
2. User fills checkout form
   ↓
3. Create Order (createRetailOrder)
   ↓
4. Create Payment Session (createPaymentSession)
   ↓
5. Redirect user to Ziina payment URL
   ↓
6. User pays on Ziina page
   ↓
7. Ziina redirects back to your site
   ↓
8. Verify Payment Status (verifyPayment)
   ↓
9. Show success/error message
```

---

## 🔄 Step-by-Step Process

### STEP 1: User Adds Items to Cart

**GraphQL Mutation:**
```graphql
mutation {
  addToCart(
    sessionKey: "user-session-123"
    productId: 1
    quantity: 2
  ) {
    success
    cart {
      total
      itemCount
    }
  }
}
```

**Result:** Cart created with items

---

### STEP 2: User Fills Checkout Form

**Required Information:**
- Customer Name
- Customer Email
- Customer Phone
- Shipping Address:
  - Full Name
  - Phone Number
  - Email
  - Address Line 1
  - City
  - Emirates (DUBAI, ABU_DHABI, etc.)
  - Postal Code (optional)

---

### STEP 3: Create Order

**GraphQL Mutation:**
```graphql
mutation CreateOrder(
  $sessionKey: String!
  $customerInfo: CustomerInput!
  $shippingAddress: AddressInput!
) {
  createRetailOrder(
    sessionKey: $sessionKey
    customerInfo: $customerInfo
    shippingAddress: $shippingAddress
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
      items {
        productName
        quantity
        unitPrice
        totalPrice
      }
    }
  }
}
```

**Variables:**
```json
{
  "sessionKey": "user-session-123",
  "customerInfo": {
    "name": "Ahmed Al Maktoum",
    "email": "ahmed@example.com",
    "phone": "+971501234567"
  },
  "shippingAddress": {
    "fullName": "Ahmed Al Maktoum",
    "phoneNumber": "+971501234567",
    "email": "ahmed@example.com",
    "addressLine1": "Villa 123, Palm Jumeirah",
    "city": "Dubai",
    "emirate": "DUBAI",
    "postalCode": "12345"
  }
}
```

**What Happens:**
- ✅ Order created with status: `PENDING`
- ✅ Order number generated (e.g., `ORD-100214CD`)
- ✅ Inventory reserved (not deducted yet)
- ✅ Cart cleared
- ✅ Order saved to database

**Save:** `orderNumber` and `order.id` for next step

---

### STEP 4: Create Payment Session

**GraphQL Mutation:**
```graphql
mutation CreatePaymentSession(
  $input: PaymentSessionInput!
  $gatewayName: String!
) {
  createPaymentSession(input: $input, gatewayName: $gatewayName) {
    success
    message
    paymentUrl
    paymentId
    expiresAt
    gatewayResponse
  }
}
```

**Variables:**
```json
{
  "input": {
    "orderId": "ORD-100214CD",
    "amount": "329.94",
    "currency": "AED",
    "customerEmail": "ahmed@example.com",
    "customerPhone": "+971501234567",
    "customerName": "Ahmed Al Maktoum",
    "taxAmount": "5.00",
    "shippingAmount": "15.00",
    "discountAmount": "0.00",
    "items": [
      {
        "name": "Lindt Excellence Dark 85%",
        "price": "49.99",
        "quantity": 6,
        "sku": "LINDT-DARK-85"
      }
    ],
    "shippingAddress": {
      "fullName": "Ahmed Al Maktoum",
      "phoneNumber": "+971501234567",
      "email": "ahmed@example.com",
      "addressLine1": "Villa 123, Palm Jumeirah",
      "city": "Dubai",
      "emirate": "DUBAI",
      "postalCode": "12345"
    }
  },
  "gatewayName": "ZIINA"
}
```

**Response:**
```json
{
  "data": {
    "createPaymentSession": {
      "success": true,
      "message": "Payment session created successfully",
      "paymentUrl": "https://pay.ziina.com/payment_intent/0ff34524-4899-4390-9e08-6615f61e78db",
      "paymentId": "0ff34524-4899-4390-9e08-6615f61e78db",
      "expiresAt": null,
      "gatewayResponse": {...}
    }
  }
}
```

**What Happens:**
- ✅ Payment record created in database
- ✅ Payment status: `PENDING`
- ✅ Payment linked to order
- ✅ Ziina payment session created
- ✅ Payment URL generated

**Save:** `paymentId` and `paymentUrl`

---

### STEP 5: Redirect User to Payment

**Action:** Redirect user to the `paymentUrl` from Step 4

**URL to Use:**
```
https://pay.ziina.com/payment_intent/0ff34524-4899-4390-9e08-6615f61e78db
```

**What Happens:**
- User is redirected to Ziina's payment page
- User enters payment details (card, Apple Pay, etc.)
- User completes or cancels payment

---

### STEP 6: User Completes Payment on Ziina

**User Actions:**
1. Enters payment method (card, Apple Pay, etc.)
2. Confirms payment
3. Payment is processed by Ziina

**Ziina Actions:**
- Processes payment
- Sends webhook to your backend (automatic)
- Redirects user back to your site

---

### STEP 7: Ziina Redirects User Back

**Redirect URLs (configured in backend):**

**Success URL:**
```
http://localhost:3000/payment/success?payment_id=0ff34524-4899-4390-9e08-6615f61e78db
```

**Cancel URL:**
```
http://localhost:3000/payment/cancel?payment_id=0ff34524-4899-4390-9e08-6615f61e78db
```

**Failure URL:**
```
http://localhost:3000/payment/failure?payment_id=0ff34524-4899-4390-9e08-6615f61e78db
```

**Important:** Get `payment_id` from URL query parameter

---

### STEP 8: Verify Payment Status

**GraphQL Mutation:**
```graphql
mutation VerifyPayment($input: PaymentVerificationInput!) {
  verifyPayment(input: $input) {
    success
    message
    status
    amount
    transactionId
    gatewayResponse
  }
}
```

**Variables:**
```json
{
  "input": {
    "paymentId": "0ff34524-4899-4390-9e08-6615f61e78db",
    "gatewayName": "ZIINA"
  }
}
```

**Response (Success):**
```json
{
  "data": {
    "verifyPayment": {
      "success": true,
      "message": "Payment verified successfully",
      "status": "completed",
      "amount": "329.94",
      "transactionId": "TXN-123456",
      "gatewayResponse": {...}
    }
  }
}
```

**Response (Cancelled):**
```json
{
  "data": {
    "verifyPayment": {
      "success": true,
      "message": "Payment verified successfully",
      "status": "cancelled",
      "amount": "329.94",
      "transactionId": null,
      "gatewayResponse": {...}
    }
  }
}
```

**What Happens:**
- ✅ Backend verifies payment with Ziina API
- ✅ Payment status updated in database
- ✅ If successful: Order status updated to `CONFIRMED`
- ✅ If successful: Inventory deducted
- ✅ Status history created

---

### STEP 9: Check Payment Status

**GraphQL Query:**
```graphql
query GetPayment($paymentId: String!) {
  payment(paymentId: $paymentId) {
    id
    paymentId
    status
    amount
    currency
    order {
      orderNumber
      status
      customerName
      totalAmount
    }
    gateway {
      name
    }
    createdAt
    capturedAt
    gatewayTransactionId
    gatewayResponse
  }
}
```

**Variables:**
```json
{
  "paymentId": "0ff34524-4899-4390-9e08-6615f61e78db"
}
```

**Use this to:**
- Display payment details
- Show order status
- Verify payment was successful

---

## 📊 Payment Status Values

### From `verifyPayment` Mutation:
- `completed` - Payment successful ✅
- `cancelled` - User cancelled ❌
- `failed` - Payment failed ❌
- `pending` - Still processing ⏳

### From `payment` Query (Database):
- `PENDING` - Payment created, awaiting completion
- `AUTHORIZED` - Payment authorized
- `CAPTURED` - Payment completed successfully ✅
- `FAILED` - Payment failed ❌
- `CANCELLED` - Payment cancelled ❌
- `REFUNDED` - Payment refunded

---

## 🔄 What Happens Automatically (Backend)

### When Payment Succeeds (via Webhook):

1. **Ziina sends webhook** to your backend
2. **Backend receives webhook** at: `/api/payments/webhooks/ziina/`
3. **Backend updates:**
   - Payment status: `PENDING` → `CAPTURED`
   - Order status: `PENDING` → `CONFIRMED`
   - Inventory: Reserved → Deducted
   - Status history: Entry created
4. **Order confirmed** automatically

### If Webhook Doesn't Work:

- Use `verifyPayment` mutation manually
- It will update payment and order status
- Inventory will be deducted

---

## ✅ Success Flow

```
1. Order Created → Status: PENDING
   ↓
2. Payment Session Created → Payment Status: PENDING
   ↓
3. User Pays on Ziina
   ↓
4. Webhook Received → Payment: CAPTURED, Order: CONFIRMED
   ↓
5. Inventory Deducted
   ↓
6. Order Ready for Processing
```

---

## ❌ Cancelled Flow

```
1. Order Created → Status: PENDING
   ↓
2. Payment Session Created → Payment Status: PENDING
   ↓
3. User Cancels on Ziina
   ↓
4. Payment Status: CANCELLED
   ↓
5. Order Remains: PENDING
   ↓
6. Inventory Still Reserved
   ↓
7. User Can Create New Payment Session
```

---

## 🔍 Verification Checklist

After payment, verify:

- [ ] Payment status is `CAPTURED` or `completed`
- [ ] Order status is `CONFIRMED`
- [ ] `capturedAt` timestamp is set
- [ ] `gatewayTransactionId` is populated
- [ ] Inventory is deducted
- [ ] Status history shows payment confirmation

---

## 📝 Complete GraphQL Queries Reference

### 1. Create Order
```graphql
mutation CreateOrder($sessionKey: String!, $customerInfo: CustomerInput!, $shippingAddress: AddressInput!) {
  createRetailOrder(sessionKey: $sessionKey, customerInfo: $customerInfo, shippingAddress: $shippingAddress) {
    success
    order {
      orderNumber
      totalAmount
    }
  }
}
```

### 2. Create Payment Session
```graphql
mutation CreatePaymentSession($input: PaymentSessionInput!, $gatewayName: String!) {
  createPaymentSession(input: $input, gatewayName: $gatewayName) {
    success
    paymentUrl
    paymentId
  }
}
```

### 3. Verify Payment
```graphql
mutation VerifyPayment($input: PaymentVerificationInput!) {
  verifyPayment(input: $input) {
    success
    status
    amount
  }
}
```

### 4. Get Payment Details
```graphql
query GetPayment($paymentId: String!) {
  payment(paymentId: $paymentId) {
    status
    amount
    order {
      orderNumber
      status
    }
    capturedAt
  }
}
```

---

## 🎯 Key Points

1. **Always verify payment** - Don't trust redirect URL alone
2. **Save payment ID** - Store it for verification
3. **Handle all statuses** - Success, cancelled, failed
4. **Check order status** - Verify order was confirmed
5. **Webhook is automatic** - But verify manually if needed

---

## 🔗 Important URLs

**GraphQL Endpoint:**
```
http://164.90.215.173/graphql/
```

**Webhook Endpoint:**
```
http://164.90.215.173/api/payments/webhooks/ziina/
```

**Payment URLs (from response):**
- Redirect: `paymentUrl` from `createPaymentSession`
- Embedded: `embedded_url` from `gatewayResponse` (optional)

---

## 📋 Field Reference

### PaymentSessionInput Fields:
- `orderId` (String) - Order number
- `amount` (Decimal) - Total amount
- `currency` (String) - Currency code (AED)
- `customerEmail` (String) - Customer email
- `customerPhone` (String) - Customer phone
- `customerName` (String) - Customer name
- `taxAmount` (Decimal) - Tax amount
- `shippingAmount` (Decimal) - Shipping fee
- `discountAmount` (Decimal) - Discount
- `items` (List) - Order items
- `shippingAddress` (Object) - Shipping address

### PaymentVerificationInput Fields:
- `paymentId` (String) - Payment ID from createPaymentSession
- `gatewayName` (String) - Gateway name (ZIINA)

---

## ✅ Complete Flow Summary

1. **Cart** → Add items
2. **Checkout** → Fill customer info
3. **Create Order** → Get order number
4. **Create Payment** → Get payment URL
5. **Redirect** → Send user to payment URL
6. **User Pays** → On Ziina page
7. **Redirect Back** → To success/cancel URL
8. **Verify Payment** → Check status
9. **Show Result** → Success or error message

---

**This is the complete payment flow!** Follow these steps in order for a successful payment integration.

