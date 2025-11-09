# 🔍 Payment to Customer Connection

## ✅ YES! Payments ARE Connected to Customers

**Connection Chain:**
```
Payment → Order → Customer Info
```

- **Payment** has `order` (ForeignKey)
- **Order** has `customer_name`, `customer_email`, `customer_phone`
- **Webhook** provides `payment_id` which links to Payment

---

## 📊 Query to See Customer from Payment

### Get All Payments with Customer Info

```graphql
query {
  payments(limit: 10) {
    id
    paymentId
    status
    amount
    currency
    createdAt
    order {
      orderNumber
      status
      customerName
      customerEmail
      customerPhone
      totalAmount
      createdAt
    }
    gateway {
      name
    }
  }
}
```

**This shows:**
- ✅ Payment ID
- ✅ Payment status
- ✅ Which customer made the payment (John Doe, etc.)
- ✅ Customer email and phone
- ✅ Order number
- ✅ Order status

---

### Get Payment by ID with Customer Info

```graphql
query {
  payment(paymentId: "your-payment-id-here") {
    id
    paymentId
    status
    amount
    order {
      orderNumber
      customerName
      customerEmail
      customerPhone
      status
      items {
        productName
        quantity
        unitPrice
      }
    }
    gateway {
      name
    }
    gatewayResponse
  }
}
```

---

### Find Payments by Customer Email

```graphql
query {
  payments(limit: 50) {
    paymentId
    status
    amount
    order {
      orderNumber
      customerName
      customerEmail
      customerPhone
    }
  }
}
```

Then filter in your code by `customerEmail == "john@example.com"`

---

## 🔄 What Happens When Webhook Arrives

### Before (Old Code):
1. ✅ Webhook received
2. ✅ Payment status updated
3. ❌ Order status NOT updated
4. ❌ Inventory NOT deducted

### After (Fixed Code):
1. ✅ Webhook received
2. ✅ Payment status updated
3. ✅ **Order status updated: PENDING → CONFIRMED**
4. ✅ **Inventory deducted automatically**
5. ✅ **Status history created**
6. ✅ **Customer identified through Payment → Order**

---

## 🧪 Test the Connection

### Step 1: Create Order & Payment
```graphql
# Create order (saves customer: John Doe)
mutation {
  createRetailOrder(...) {
    order {
      orderNumber
      customerName
    }
  }
}

# Create payment session
mutation {
  createPaymentSession(...) {
    paymentId
  }
}
```

### Step 2: Pay on Ziina
- Use test card
- Payment succeeds

### Step 3: Webhook Arrives
- Webhook finds Payment by `payment_id`
- Gets Order from Payment
- Updates Order status
- **Logs customer name**: `"Order ORD-XXX confirmed for customer John Doe"`

### Step 4: Query to Verify
```graphql
query {
  payment(paymentId: "your-payment-id") {
    order {
      customerName
      customerEmail
      status  # Should be CONFIRMED now
    }
  }
}
```

---

## 📋 Webhook Payload Structure

When Ziina sends webhook, it contains:

```json
{
  "payment_id": "ZIINA-123456",
  "status": "completed",
  "amount": "119.98",
  "currency": "AED",
  "transaction_id": "TXN-789",
  "customer_email": "john@example.com",  // Optional
  "customer_phone": "+971501234567",      // Optional
  "timestamp": "2025-11-09T10:00:00Z"
}
```

**Your system:**
1. Receives webhook with `payment_id`
2. Finds Payment in database using `payment_id`
3. Gets Order from `payment.order`
4. Gets Customer from `order.customer_name`, `order.customer_email`
5. Updates everything automatically

---

## ✅ Summary

**YES, you CAN identify the customer from webhooks:**

1. **Webhook provides:** `payment_id`
2. **Your system finds:** Payment by `payment_id`
3. **Payment has:** `order` (ForeignKey)
4. **Order has:** `customer_name`, `customer_email`, `customer_phone`
5. **Result:** You know exactly which customer (John Doe) made the payment!

**The fix I just made:**
- ✅ Webhook now automatically updates Order status
- ✅ Webhook now automatically deducts inventory
- ✅ Webhook logs customer name in the status history
- ✅ Everything is connected: Payment → Order → Customer

---

## 🎯 Example Query Result

```json
{
  "data": {
    "payments": [
      {
        "paymentId": "PAY-ABC123",
        "status": "COMPLETED",
        "amount": "119.98",
        "order": {
          "orderNumber": "ORD-8B7FF47E",
          "customerName": "John Doe",
          "customerEmail": "john@example.com",
          "customerPhone": "+971501234567",
          "status": "CONFIRMED"
        }
      }
    ]
  }
}
```

**You can see:** John Doe made payment PAY-ABC123 for order ORD-8B7FF47E!

---

**Everything is connected!** 🎉

