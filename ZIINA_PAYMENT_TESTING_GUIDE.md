# Ziina Payment Testing Guide

Complete step-by-step guide to test Ziina payment integration using Postman.

---

## 📋 Prerequisites

1. **Django server running**
   ```bash
   python manage.py runserver
   ```

2. **Ziina credentials configured** in `.env`:
   - `ZIINA_API_KEY` ✅ (you have this)
   - `ZIINA_MERCHANT_ID` (if available)
   - `ZIINA_TEST_MODE=True` (for testing)

3. **Postman collection imported** (`POSTMAN_COLLECTION.json`)

---

## 🧪 Complete Testing Flow

### **Step 1: Authenticate (Optional - for admin operations)**

**Request:** `🔐 Authentication > Login - Get JWT Token`

**What it does:**
- Gets JWT token for admin operations
- Saves token to `{{jwt_token}}` variable

**Expected Response:**
```json
{
  "data": {
    "tokenAuth": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "user": {
        "id": "1",
        "username": "choco"
      }
    }
  }
}
```

**Note:** Payment mutations don't require authentication, but it's good to have the token ready.

---

### **Step 2: Get Products (Optional - to get product IDs)**

**Request:** `📦 Queries - Products > Get All Products`

**What it does:**
- Lists all available products
- Use this to get product IDs for cart testing

**Expected Response:**
```json
{
  "data": {
    "products": [
      {
        "id": 1,
        "name": "Premium Chocolate Box",
        "sku": "CHOC-001",
        ...
      }
    ]
  }
}
```

---

### **Step 3: Add Items to Cart**

**Request:** `🛒 Mutations - Customer - Cart > Add to Cart`

**Variables to set:**
- `sessionKey`: Leave empty (will auto-generate) OR use a custom session key
- `productId`: Use a product ID from Step 2 (e.g., `1`)
- `quantity`: `2`
- `variantId`: `null` (if no variant)

**What it does:**
- Creates/updates cart with items
- Auto-generates `session_key` if empty
- Saves `session_key` to `{{session_id}}` variable

**Expected Response:**
```json
{
  "data": {
    "addToCart": {
      "success": true,
      "message": "Item added to cart successfully",
      "cart": {
        "sessionKey": "abc-123-def-456",
        "total": "210.00",
        "itemCount": 2
      }
    }
  }
}
```

**Important:** Note the `sessionKey` - you'll need it for the next steps!

---

### **Step 4: Create Order**

**Request:** `📝 Mutations - Customer - Orders > Create Retail Order`

**What it does:**
- Creates an order from the cart
- Uses `{{session_id}}` from previous step
- Returns order details including `orderNumber`

**Expected Response:**
```json
{
  "data": {
    "createRetailOrder": {
      "success": true,
      "message": "Order created successfully: ORD-12345",
      "order": {
        "id": 1,
        "orderNumber": "ORD-12345",
        "totalAmount": "210.00",
        "status": "PENDING",
        ...
      }
    }
  }
}
```

**Important:** Copy the `orderNumber` (e.g., `ORD-12345`) - you'll need it for payment!

**Manual Step:** Update `{{order_id}}` variable in Postman:
1. Click on collection variables (top right)
2. Set `order_id` = `ORD-12345` (or whatever order number you got)

---

### **Step 5: Create Payment Session (Ziina)**

**Request:** `💳 Payments - Ziina > STEP 1: Create Payment Session (Ziina)`

**What it does:**
- Creates a payment session with Ziina
- Returns `paymentUrl` to redirect user
- Saves `paymentId` to `{{payment_id}}` variable

**Variables used:**
- `{{order_id}}` - From Step 4 (e.g., `ORD-12345`)
- Other fields are pre-filled in the request

**Expected Response:**
```json
{
  "data": {
    "createPaymentSession": {
      "success": true,
      "message": "Payment session created successfully",
      "paymentUrl": "https://pay.ziina.com/payment/xyz123",
      "paymentId": "ZIINA_PAY_123456",
      "expiresAt": "2024-01-15T10:30:00Z"
    }
  }
}
```

**If you get an error:**
- Check if `ZIINA_API_KEY` is set in `.env`
- Check if `ZIINA_MERCHANT_ID` is set (might be required)
- Check server logs for detailed error messages
- Verify order exists with the provided `order_id`

---

### **Step 6: Test Payment URL (Manual)**

**What to do:**
1. Copy the `paymentUrl` from Step 5
2. Open it in your browser
3. Complete the payment on Ziina's payment page
   - Use test card numbers (Ziina will provide these)
   - Or cancel to test cancellation flow

**Note:** If you don't have test credentials, you can still verify the URL was created correctly.

---

### **Step 7: Verify Payment Status**

**Request:** `💳 Payments - Ziina > STEP 2: Verify Payment Status`

**What it does:**
- Checks payment status with Ziina API
- Uses `{{payment_id}}` from Step 5
- Updates payment record in database

**Expected Response (if payment completed):**
```json
{
  "data": {
    "verifyPayment": {
      "success": true,
      "message": "Payment verified successfully",
      "status": "completed",
      "amount": "105.00",
      "transactionId": "TXN_789012"
    }
  }
}
```

**Possible Status Values:**
- `pending` - Payment is being processed
- `completed` - Payment successful ✅
- `failed` - Payment failed ❌
- `cancelled` - Payment cancelled by user

---

### **Step 8: Query Payment Details**

**Request:** `💳 Payments - Ziina > Get Payment by ID`

**What it does:**
- Gets full payment details from database
- Shows all payment information

**Expected Response:**
```json
{
  "data": {
    "payment": {
      "id": 1,
      "paymentId": "ZIINA_PAY_123456",
      "orderId": "ORD-12345",
      "gateway": "ZIINA",
      "status": "completed",
      "amount": "105.00",
      "currency": "AED",
      "transactionId": "TXN_789012",
      "createdAt": "2024-01-15T10:00:00Z",
      "verifiedAt": "2024-01-15T10:05:00Z"
    }
  }
}
```

---

## 🔍 Quick Test (Minimal Flow)

If you just want to test payment creation quickly:

1. **Set `order_id` variable manually:**
   - Use any order number (e.g., `"ORD-TEST-123"`)
   - Or create a real order first (Steps 1-4)

2. **Create Payment Session:**
   - Request: `💳 Payments - Ziina > STEP 1: Create Payment Session (Ziina)`
   - Check if `paymentUrl` is returned

3. **Verify Payment:**
   - Request: `💳 Payments - Ziina > STEP 2: Verify Payment Status`
   - Check payment status

---

## ✅ Success Checklist

After testing, verify:

- [ ] Payment session created successfully
- [ ] `paymentUrl` is returned and valid
- [ ] `paymentId` is saved to variables
- [ ] Payment can be verified
- [ ] Payment status is correct
- [ ] Payment record exists in database

---

## 🚨 Common Issues & Solutions

### **Issue 1: "Unknown type 'PaymentSessionInput'"**

**Solution:**
- Restart Django server
- Check that `payments.schema` is imported in `ecomarce_choco/schema.py`

### **Issue 2: "Variable '$input' got invalid value"**

**Solution:**
- Check field names use snake_case (e.g., `order_id`, not `orderId`)
- Verify `items` and `shipping_address` are objects, not strings
- Check Postman collection is up to date

### **Issue 3: "Payment session creation failed"**

**Possible causes:**
- Missing `ZIINA_API_KEY` in `.env`
- Missing `ZIINA_MERCHANT_ID` (might be required)
- Invalid order ID
- Network error connecting to Ziina API

**Solution:**
- Check `.env` file has all Ziina credentials
- Check server logs for detailed error
- Verify order exists
- Check internet connection

### **Issue 4: "Authentication required"**

**Solution:**
- Payment mutations don't require auth, but if you see this:
- Check if you accidentally added auth to the request
- Remove `Authorization` header from payment requests

### **Issue 5: Payment URL doesn't work**

**Solution:**
- Check if `ZIINA_TEST_MODE=True` in `.env`
- Verify `ZIINA_BASE_URL` is correct
- Check Ziina dashboard for test credentials
- Contact Ziina support for test environment access

---

## 📝 Testing Without Real Payment

You can test the integration without completing actual payment:

1. **Create Payment Session** ✅
   - Verify `paymentUrl` is returned
   - Check `paymentId` is generated

2. **Verify Payment (before payment)**
   - Status should be `pending`

3. **Check Database**
   - Payment record should exist with `status='pending'`

4. **Test Error Handling**
   - Try with invalid order ID
   - Try with missing fields
   - Verify error messages are clear

---

## 🎯 Expected Test Results

### **Successful Flow:**
```
1. Create Payment Session → ✅ success: true, paymentUrl returned
2. Verify Payment (before) → ✅ status: "pending"
3. Complete Payment (manual) → User completes on Ziina
4. Verify Payment (after) → ✅ status: "completed"
5. Query Payment → ✅ All details correct
```

### **Error Scenarios:**
```
1. Invalid order ID → ❌ Error: "Order not found"
2. Missing API key → ❌ Error: "Ziina API error"
3. Invalid amount → ❌ Error: "Invalid order data"
```

---

## 🔗 Related Documentation

- **Frontend Integration:** `ZIINA_FRONTEND_INTEGRATION.md`
- **Payment Gateway Setup:** `PAYMENT_GATEWAY_SETUP.md`
- **Postman Collection:** `POSTMAN_COLLECTION.json`

---

## 💡 Tips

1. **Use Test Mode:** Always set `ZIINA_TEST_MODE=True` during development
2. **Check Logs:** Django server logs show detailed error messages
3. **Save Variables:** Postman automatically saves `payment_id` and `order_id`
4. **Test Incrementally:** Test each step before moving to the next
5. **Use Real Order:** Create a real order first for more realistic testing

---

**Ready to test?** Start with Step 1 and work through each step! 🚀

