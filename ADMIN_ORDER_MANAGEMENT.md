# 📦 Admin Order Management Guide

Complete guide for managing orders as an admin user.

---

## 🔐 Authentication Required

All admin operations require:
- **JWT Token** in the `Authorization` header
- **Staff user** (user must have `is_staff=True`)

**Header Format:**
```
Authorization: Bearer <your-jwt-token>
```

---

## 📊 Viewing Orders

### 1. Get All Orders

View all orders in the system with optional filters.

**Query:** `orders`

**Arguments:**
- `status` (String, optional) - Filter by status: `PENDING`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`
- `order_type` (String, optional) - Filter by type: `RETAIL`, `WHOLESALE`
- `limit` (Int, optional) - Limit number of results (default: all)

**Example - All Orders:**
```graphql
query {
  orders {
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
    currency
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
      city
      emirate
      addressLine1
    }
  }
}
```

**Example - Filter by Status:**
```graphql
query {
  orders(status: "PENDING", limit: 20) {
    id
    orderNumber
    status
    customerName
    totalAmount
    createdAt
  }
}
```

**Example - Filter by Type:**
```graphql
query {
  orders(order_type: "RETAIL", limit: 50) {
    id
    orderNumber
    status
    totalAmount
  }
}
```

**Example - Recent Orders:**
```graphql
query {
  orders(limit: 10) {
    id
    orderNumber
    status
    customerName
    totalAmount
    createdAt
  }
}
```

---

### 2. Get Single Order Details

View complete details of a specific order by order number.

**Query:** `order`

**Arguments:**
- `order_number` (String, required) - The order number (e.g., `ORD-8B7FF47E`)

**Example:**
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
    customerCompany
    subtotal
    discountAmount
    taxAmount
    deliveryFee
    totalAmount
    currency
    notes
    internalNotes
    createdAt
    updatedAt
    confirmedAt
    deliveredAt
    cancelledAt
    items {
      id
      product {
        id
        name
        sku
      }
      variant {
        id
        sku
      }
      productName
      productSku
      variantOptions
      quantity
      unitPrice
      discountAmount
      taxAmount
      totalPrice
    }
    shippingAddress {
      id
      fullName
      phoneNumber
      email
      addressLine1
      addressLine2
      city
      emirate
      area
      postalCode
      country
      deliveryInstructions
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

---

## ✅ Managing Order Status

### 3. Update Order Status

Change the status of an order and add notes. Automatically creates a status history entry.

**Mutation:** `updateOrderStatus`

**Input Fields:**
- `order_id` (Int, required) - Order ID (not order number)
- `status` (String, required) - New status (see valid statuses below)
- `notes` (String, optional) - Notes about the status change

**Valid Statuses:**
- `PENDING` - Order received, awaiting payment
- `CONFIRMED` - Payment confirmed
- `PROCESSING` - Order being prepared
- `SHIPPED` - Order dispatched
- `DELIVERED` - Order delivered to customer
- `CANCELLED` - Order cancelled

**Example - Confirm Order:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "Payment verified via Ziina - Transaction ID: ZIINA-123456"
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

**Example - Mark as Processing:**
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
    }
  }
}
```

**Example - Ship Order:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "SHIPPED"
    notes: "Shipped via Aramex - Tracking Number: AE123456789 - Expected delivery: 2-3 business days"
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

**Example - Mark as Delivered:**
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "DELIVERED"
    notes: "Delivered successfully to customer - Signature received at 14:30"
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

### 4. Cancel Order

Cancel an order. Cannot cancel orders with status `DELIVERED` or `CANCELLED`. Automatically returns inventory to stock.

**Mutation:** `cancelOrder`

**Arguments:**
- `order_id` (Int, required) - Order ID
- `reason` (String, optional) - Reason for cancellation

**Example:**
```graphql
mutation {
  cancelOrder(
    orderId: 1
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

**Important Notes:**
- ✅ Automatically returns inventory to stock
- ✅ Creates status history entry
- ❌ Cannot cancel `DELIVERED` orders
- ❌ Cannot cancel already `CANCELLED` orders

---

## 📍 Updating Shipping Information

### 5. Update Shipping Address

Update the shipping address for an order. All fields are optional - only provided fields will be updated.

**Mutation:** `updateShippingAddress`

**Arguments:**
- `order_id` (Int, required) - Order ID
- `full_name` (String, optional)
- `phone_number` (String, optional)
- `address_line1` (String, optional)
- `address_line2` (String, optional)
- `city` (String, optional)
- `emirate` (String, optional) - Must be uppercase: `DUBAI`, `ABU_DHABI`, `SHARJAH`, etc.
- `postal_code` (String, optional)

**Valid Emirates:**
- `DUBAI`
- `ABU_DHABI`
- `SHARJAH`
- `AJMAN`
- `UMM_AL_QUWAIN`
- `RAS_AL_KHAIMAH`
- `FUJAIRAH`

**Example - Update Full Address:**
```graphql
mutation {
  updateShippingAddress(
    orderId: 1
    fullName: "Ahmed Abdullah Al Maktoum"
    phoneNumber: "+971509876543"
    addressLine1: "Villa 456, Jumeirah Beach Residence"
    addressLine2: "Building 12, Floor 3, Apartment 301"
    city: "Dubai"
    emirate: "DUBAI"
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
        createdAt
      }
    }
  }
}
```

**Example - Update Only Phone Number:**
```graphql
mutation {
  updateShippingAddress(
    orderId: 1
    phoneNumber: "+971501112233"
  ) {
    success
    message
    order {
      shippingAddress {
        fullName
        phoneNumber
      }
    }
  }
}
```

**Note:** This automatically creates a status history entry with note "Shipping address updated".

---

## 📋 Common Workflows

### Workflow 1: Process New Order

```graphql
# Step 1: View pending orders
query {
  orders(status: "PENDING") {
    id
    orderNumber
    customerName
    totalAmount
    createdAt
  }
}

# Step 2: Confirm payment
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "Payment verified"
  }) {
    success
    order { orderNumber status }
  }
}

# Step 3: Start processing
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "PROCESSING"
    notes: "Preparing order"
  }) {
    success
  }
}

# Step 4: Ship order
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "SHIPPED"
    notes: "Shipped via Aramex - Tracking: AE123456"
  }) {
    success
  }
}

# Step 5: Mark as delivered
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "DELIVERED"
    notes: "Delivered successfully"
  }) {
    success
  }
}
```

---

### Workflow 2: Handle Customer Address Change

```graphql
# Step 1: Get order details
query {
  order(orderNumber: "ORD-8B7FF47E") {
    id
    shippingAddress {
      fullName
      addressLine1
      city
      emirate
    }
  }
}

# Step 2: Update address
mutation {
  updateShippingAddress(
    orderId: 1
    addressLine1: "New Address 123"
    city: "Dubai"
    emirate: "DUBAI"
  ) {
    success
    message
  }
}
```

---

### Workflow 3: Cancel Order and Restore Inventory

```graphql
# Step 1: Cancel order
mutation {
  cancelOrder(
    orderId: 1
    reason: "Customer requested cancellation"
  ) {
    success
    message
    order {
      orderNumber
      status
    }
  }
}

# Step 2: Verify inventory restored (check product)
query {
  product(id: 5) {
    name
    inventory {
      quantityInStock
    }
  }
}
```

---

## 🔍 Advanced Queries

### Filter Orders by Multiple Criteria

```graphql
# Get recent retail orders that are pending
query {
  orders(order_type: "RETAIL", status: "PENDING", limit: 10) {
    id
    orderNumber
    customerName
    totalAmount
    createdAt
  }
}
```

### View Order Status History

```graphql
query {
  order(orderNumber: "ORD-8B7FF47E") {
    orderNumber
    status
    statusHistory {
      status
      notes
      createdAt
    }
  }
}
```

### Get Order with All Related Data

```graphql
query {
  order(orderNumber: "ORD-8B7FF47E") {
    id
    orderNumber
    status
    customerName
    customerEmail
    customerPhone
    totalAmount
    items {
      productName
      productSku
      quantity
      unitPrice
      totalPrice
      variantOptions
    }
    shippingAddress {
      fullName
      phoneNumber
      email
      addressLine1
      addressLine2
      city
      emirate
      area
      postalCode
      deliveryInstructions
    }
    statusHistory {
      status
      notes
      createdAt
    }
  }
}
```

---

## 📊 Order Status Flow

```
📦 ORDER LIFECYCLE:

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

**Allowed Transitions:**
- ✅ PENDING → CONFIRMED
- ✅ CONFIRMED → PROCESSING
- ✅ PROCESSING → SHIPPED
- ✅ SHIPPED → DELIVERED
- ✅ Any status (except DELIVERED) → CANCELLED

**Not Allowed:**
- ❌ DELIVERED → CANCELLED
- ❌ CANCELLED → Any other status

---

## 💡 Best Practices

### 1. Always Add Notes
When updating order status, always include helpful notes:
```graphql
notes: "Shipped via Aramex - Tracking: AE123456 - Expected: 2-3 days"
```

### 2. Verify Before Cancelling
Check order status before cancelling:
```graphql
query {
  order(orderNumber: "ORD-8B7FF47E") {
    status
  }
}
```

### 3. Use Order ID, Not Order Number
For mutations, use the numeric `order_id`, not the `order_number` string:
- ✅ `orderId: 1` (correct)
- ❌ `orderId: "ORD-8B7FF47E"` (incorrect)

### 4. Track Status Changes
Always check `statusHistory` to see the complete order timeline:
```graphql
statusHistory {
  status
  notes
  createdAt
}
```

### 5. Filter Orders Efficiently
Use filters to reduce data load:
```graphql
orders(status: "PENDING", limit: 20)  # Only pending orders, max 20
```

---

## 🚨 Error Handling

### Common Errors

**1. Not Authorized**
```
"Not authorized"
```
**Solution:** Ensure you're logged in with a staff account and JWT token is valid.

**2. Order Not Found**
```
"Order not found"
```
**Solution:** Check the order ID or order number is correct.

**3. Invalid Status**
```
"Invalid status. Valid options: PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED"
```
**Solution:** Use one of the valid status values (all uppercase).

**4. Cannot Cancel Order**
```
"Cannot cancel order with status: DELIVERED"
```
**Solution:** Cannot cancel delivered or already cancelled orders.

---

## 📝 Order Fields Reference

### Order Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Int | Order ID (use for mutations) |
| `orderNumber` | String | Unique order number (e.g., "ORD-8B7FF47E") |
| `status` | String | Current status |
| `orderType` | String | Order type (RETAIL, WHOLESALE) |
| `customerName` | String | Customer name |
| `customerEmail` | String | Customer email |
| `customerPhone` | String | Customer phone |
| `customerCompany` | String | Company name (if applicable) |
| `subtotal` | Decimal | Subtotal before tax and delivery |
| `discountAmount` | Decimal | Discount applied |
| `taxAmount` | Decimal | VAT amount (5% in UAE) |
| `deliveryFee` | Decimal | Delivery fee |
| `totalAmount` | Decimal | Total amount |
| `currency` | String | Currency code (AED) |
| `notes` | String | Customer notes |
| `internalNotes` | String | Staff-only notes |
| `createdAt` | DateTime | Order creation time |
| `updatedAt` | DateTime | Last update time |
| `confirmedAt` | DateTime | Payment confirmation time |
| `deliveredAt` | DateTime | Delivery time |
| `cancelledAt` | DateTime | Cancellation time |
| `items` | List | Order items |
| `shippingAddress` | Object | Shipping address |
| `statusHistory` | List | Status change history |

---

## 🎯 Quick Reference

### View Orders
```graphql
query { orders { id orderNumber status totalAmount } }
```

### Get Order Details
```graphql
query { order(orderNumber: "ORD-XXX") { ... } }
```

### Update Status
```graphql
mutation {
  updateOrderStatus(input: {
    orderId: 1
    status: "CONFIRMED"
    notes: "..."
  }) { success }
}
```

### Cancel Order
```graphql
mutation {
  cancelOrder(orderId: 1, reason: "...") { success }
}
```

### Update Address
```graphql
mutation {
  updateShippingAddress(orderId: 1, ...) { success }
}
```

---

## ✅ Checklist

- [ ] Can view all orders
- [ ] Can filter orders by status
- [ ] Can filter orders by type
- [ ] Can view single order details
- [ ] Can update order status
- [ ] Can cancel orders
- [ ] Can update shipping address
- [ ] Understands status flow
- [ ] Knows when cancellation is allowed
- [ ] Knows inventory is auto-restored on cancel

---

**Ready to manage orders!** 🚀

