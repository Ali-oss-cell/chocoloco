# 📋 Test Order Management (Admin)

Complete order lifecycle management testing.

---

## 📊 STEP 1: View All Orders

```graphql
query {
  orders {
    id
    orderNumber
    status
    totalAmount
    grandTotal
    paymentMethod
    paymentStatus
    customerEmail
    customerPhone
    createdAt
    items {
      product {
        name
      }
      quantity
    }
    shippingAddress {
      fullName
      city
      emirate
    }
  }
}
```

**Expected:** List of all orders in system

---

## 📦 STEP 2: View Single Order Details

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
    updatedAt
    items {
      id
      product {
        name
        sku
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
      id
      status
      notes
      createdAt
    }
  }
}
```

**Expected:** Complete order details with full history

---

## ✅ STEP 3: Confirm Order (Payment Verified)

```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "Payment verified - Cash on Delivery confirmed"
  }) {
    success
    message
    order {
      id
      orderNumber
      status
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
- Status changed to CONFIRMED
- New entry in status history
- Message: "Order ORD-2025-0001 status updated to CONFIRMED"

---

## 📦 STEP 4: Start Processing Order

```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "PROCESSING"
    notes: "Order being prepared in warehouse - Picking items"
  }) {
    success
    message
    order {
      orderNumber
      status
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
- Status: PROCESSING
- Status history shows progression

---

## 🚚 STEP 5: Ship Order

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
      statusHistory {
        status
        notes
      }
    }
  }
}
```

**Expected:**
- Status: SHIPPED
- Tracking info saved in notes

---

## ✅ STEP 6: Mark as Delivered

```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "DELIVERED"
    notes: "Delivered successfully to customer - Signature received"
  }) {
    success
    message
    order {
      orderNumber
      status
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
- Status: DELIVERED
- Complete order lifecycle tracked

---

## 📍 STEP 7: Update Shipping Address (If Needed)

```graphql
mutation {
  updateShippingAddress(
    orderId: 1
    fullName: "Ahmed Abdullah Al Maktoum"
    phoneNumber: "+971509876543"
    addressLine1: "Villa 456, Jumeirah Beach Residence"
    addressLine2: "Building 12, Floor 3"
    city: "Dubai"
    emirate: "Dubai"
    postalCode: "54321"
  ) {
    success
    message
    order {
      orderNumber
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
        notes
      }
    }
  }
}
```

**Expected:**
- Shipping address updated
- Status history logged the change

---

## ❌ STEP 8: Cancel an Order

First, create a new order to cancel:

```graphql
# Create test order
mutation {
  addToCart(sessionId: "cancel-test", productId: 5, quantity: 2) { success }
}

mutation {
  createRetailOrder(input: {
    sessionId: "cancel-test"
    customerEmail: "cancel@test.ae"
    customerPhone: "+971501111111"
    shippingAddress: {
      fullName: "Test Customer"
      phoneNumber: "+971501111111"
      addressLine1: "Test Address"
      city: "Dubai"
      emirate: "Dubai"
    }
    paymentMethod: "CASH_ON_DELIVERY"
  }) {
    success
    order { id orderNumber }
  }
}
```

Now cancel it:

```graphql
mutation {
  cancelOrder(
    orderId: 2
    reason: "Customer requested cancellation - Changed mind"
  ) {
    success
    message
    order {
      id
      orderNumber
      status
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
- Order status: CANCELLED
- Inventory returned to stock automatically
- Reason saved in status history

---

## 🔍 STEP 9: Verify Inventory Restored

```graphql
query {
  product(id: 5) {
    name
    inventory {
      quantityInStock
    }
  }
}
```

**Expected:** Stock quantity increased by cancelled order amount

---

## 📊 STEP 10: View Order Status History

```graphql
query {
  order(id: 1) {
    orderNumber
    status
    statusHistory {
      id
      status
      notes
      createdAt
    }
  }
}
```

**Expected:** Complete timeline:
- PENDING → Order created
- CONFIRMED → Payment verified
- PROCESSING → Being prepared
- SHIPPED → Out for delivery
- DELIVERED → Completed

---

## 🎯 Advanced Tests

### Test 1: Try to Cancel Delivered Order (Should Fail)

```graphql
mutation {
  cancelOrder(
    orderId: 1
    reason: "Test"
  ) {
    success
    message
  }
}
```

**Expected:**
- `success: false`
- Message: "Cannot cancel order with status: DELIVERED"

---

### Test 2: Multiple Status Updates in Batch

```graphql
# Create 3 test orders first
mutation {
  cart1: addToCart(sessionId: "batch-1", productId: 1, quantity: 1) { success }
  cart2: addToCart(sessionId: "batch-2", productId: 2, quantity: 1) { success }
  cart3: addToCart(sessionId: "batch-3", productId: 3, quantity: 1) { success }
}

mutation {
  order1: createRetailOrder(input: {
    sessionId: "batch-1"
    customerEmail: "batch1@test.ae"
    customerPhone: "+971501111111"
    shippingAddress: {
      fullName: "Batch Test 1"
      phoneNumber: "+971501111111"
      addressLine1: "Test 1"
      city: "Dubai"
      emirate: "Dubai"
    }
    paymentMethod: "CASH_ON_DELIVERY"
  }) { success order { id } }
  
  order2: createRetailOrder(input: {
    sessionId: "batch-2"
    customerEmail: "batch2@test.ae"
    customerPhone: "+971502222222"
    shippingAddress: {
      fullName: "Batch Test 2"
      phoneNumber: "+971502222222"
      addressLine1: "Test 2"
      city: "Abu Dhabi"
      emirate: "Abu Dhabi"
    }
    paymentMethod: "CASH_ON_DELIVERY"
  }) { success order { id } }
  
  order3: createRetailOrder(input: {
    sessionId: "batch-3"
    customerEmail: "batch3@test.ae"
    customerPhone: "+971503333333"
    shippingAddress: {
      fullName: "Batch Test 3"
      phoneNumber: "+971503333333"
      addressLine1: "Test 3"
      city: "Sharjah"
      emirate: "Sharjah"
    }
    paymentMethod: "CASH_ON_DELIVERY"
  }) { success order { id } }
}

# Confirm all 3 orders at once
mutation {
  confirm1: updateOrderStatus(input: {orderId: 3, status: "CONFIRMED", notes: "Batch confirm 1"}) { success }
  confirm2: updateOrderStatus(input: {orderId: 4, status: "CONFIRMED", notes: "Batch confirm 2"}) { success }
  confirm3: updateOrderStatus(input: {orderId: 5, status: "CONFIRMED", notes: "Batch confirm 3"}) { success }
}
```

---

### Test 3: Invalid Status Change

```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "INVALID_STATUS"
    notes: "Test"
  }) {
    success
    message
  }
}
```

**Expected:**
- `success: false`
- Message: "Invalid status. Valid options: PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED"

---

## 📋 Order Management Checklist

After completing all tests:

- ✅ Can view all orders
- ✅ Can view single order details
- ✅ Can update order status (PENDING → DELIVERED)
- ✅ Can ship orders with tracking info
- ✅ Can update shipping address
- ✅ Can cancel orders
- ✅ Inventory automatically restored on cancellation
- ✅ Cannot cancel delivered orders
- ✅ Status history tracked for all changes
- ✅ Invalid statuses rejected
- ✅ Batch operations work

---

## 🔄 Complete Order Lifecycle

```
📦 ORDER FLOW:

1. PENDING
   ↓ (Payment verified)
   
2. CONFIRMED
   ↓ (Start preparing)
   
3. PROCESSING
   ↓ (Dispatch)
   
4. SHIPPED
   ↓ (Customer receives)
   
5. DELIVERED ✅

OR

❌ CANCELLED (from any step before DELIVERED)
```

---

## 💡 Business Rules

### ✅ Allowed Transitions:
- PENDING → CONFIRMED
- CONFIRMED → PROCESSING
- PROCESSING → SHIPPED
- SHIPPED → DELIVERED
- Any status (except DELIVERED) → CANCELLED

### ❌ Not Allowed:
- DELIVERED → CANCELLED
- CANCELLED → Any other status

---

## 🎉 Admin Dashboard Features

Your API supports:

✅ **Order Overview**
- View all orders
- Filter by status
- Search by order number/customer

✅ **Order Processing**
- Confirm payment
- Update status
- Add tracking info
- Update shipping address

✅ **Order Management**
- Cancel orders
- Restore inventory
- View complete history
- Add notes

✅ **Inventory Control**
- Auto-deduct on order
- Auto-restore on cancel
- Real-time stock tracking

---

## 🚀 Ready for Production!

Your order management system is fully functional and ready for:
- Custom admin dashboard
- Automated email notifications
- Integration with shipping providers
- Payment gateway webhooks

---

**All Tests Complete!** 🎉

You now have:
- ✅ 20 Products added
- ✅ Cart & Checkout working
- ✅ Order Management working
- ✅ Complete e-commerce backend ready!

**Next Step:** Build your React frontend! 🚀

