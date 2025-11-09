# 💳 Frontend Ziina Payment Integration Guide

Complete step-by-step guide for integrating Ziina payments in your frontend application.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Complete Payment Flow](#complete-payment-flow)
3. [GraphQL Setup](#graphql-setup)
4. [Step-by-Step Implementation](#step-by-step-implementation)
5. [Code Examples](#code-examples)
6. [Error Handling](#error-handling)
7. [Testing](#testing)

---

## 🎯 Overview

**Ziina** is a UAE Central Bank licensed instant payment gateway that supports:
- ✅ Credit/Debit Cards
- ✅ Apple Pay
- ✅ Instant bank transfers
- ✅ Real-time payment processing

**Your Backend API:** `http://164.90.215.173/graphql/`

---

## 🔄 Complete Payment Flow

```
1. User adds items to cart
   ↓
2. User fills checkout form (name, email, phone, address)
   ↓
3. Frontend: Create Order (createRetailOrder)
   ↓
4. Frontend: Create Payment Session (createPaymentSession)
   ↓
5. Frontend: Redirect to Ziina payment URL
   ↓
6. User pays on Ziina page
   ↓
7. Ziina redirects back to your success/cancel/failure page
   ↓
8. Frontend: Verify Payment Status
   ↓
9. Show success/error message to user
```

---

## 🔧 GraphQL Setup

### 1. Install GraphQL Client

**For React/Next.js:**
```bash
npm install @apollo/client graphql
```

**For Vue.js:**
```bash
npm install @apollo/client graphql @vue/apollo-composable
```

### 2. Configure Apollo Client

```javascript
// apolloClient.js
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: 'http://164.90.215.173/graphql/',
});

const authLink = setContext((_, { headers }) => {
  // Get token from localStorage if needed (for admin operations)
  const token = localStorage.getItem('jwt_token');
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  }
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache()
});

export default client;
```

---

## 📝 Step-by-Step Implementation

### STEP 1: Create Order from Cart

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

---

### STEP 2: Create Payment Session

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
    "orderId": "ORD-8B7FF47E",
    "amount": "119.98",
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
        "quantity": 2,
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
      "paymentUrl": "https://pay.ziina.com/payment/xyz123",
      "paymentId": "PAY-ABC123XYZ",
      "expiresAt": "2025-11-09T12:00:00Z"
    }
  }
}
```

---

### STEP 3: Redirect to Payment

After receiving `paymentUrl`, redirect the user:

```javascript
if (data.createPaymentSession.success) {
  // Save payment ID for later verification
  localStorage.setItem('payment_id', data.createPaymentSession.paymentId);
  localStorage.setItem('order_number', order.orderNumber);
  
  // Redirect to Ziina payment page
  window.location.href = data.createPaymentSession.paymentUrl;
}
```

---

### STEP 4: Handle Payment Callback

Ziina will redirect to your configured URLs:
- **Success:** `{FRONTEND_URL}/payment/success?payment_id={payment_id}`
- **Cancel:** `{FRONTEND_URL}/payment/cancel?payment_id={payment_id}`
- **Failure:** `{FRONTEND_URL}/payment/failure?payment_id={payment_id}`

---

### STEP 5: Verify Payment Status

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
    authorizedAt
    failedAt
    gatewayTransactionId
    gatewayResponse
  }
}
```

**Always verify payment status!** Don't trust URL parameters alone.

---

## 💻 Code Examples

### React/Next.js Complete Example

```javascript
// hooks/usePayment.js
import { useState } from 'react';
import { useMutation, useQuery } from '@apollo/client';
import { gql } from '@apollo/client';

const CREATE_ORDER = gql`
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
        totalAmount
        items {
          productName
          quantity
          unitPrice
        }
      }
    }
  }
`;

const CREATE_PAYMENT = gql`
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
    }
  }
`;

const GET_PAYMENT = gql`
  query GetPayment($paymentId: String!) {
    payment(paymentId: $paymentId) {
      id
      paymentId
      status
      amount
      order {
        orderNumber
        status
      }
    }
  }
`;

export function usePayment() {
  const [createOrder] = useMutation(CREATE_ORDER);
  const [createPayment] = useMutation(CREATE_PAYMENT);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const processPayment = async (cartData, customerInfo, shippingAddress) => {
    setLoading(true);
    setError(null);

    try {
      // Step 1: Create Order
      const orderResult = await createOrder({
        variables: {
          sessionKey: cartData.sessionKey,
          customerInfo: {
            name: customerInfo.name,
            email: customerInfo.email,
            phone: customerInfo.phone,
          },
          shippingAddress: {
            fullName: shippingAddress.fullName,
            phoneNumber: shippingAddress.phoneNumber,
            email: shippingAddress.email,
            addressLine1: shippingAddress.addressLine1,
            addressLine2: shippingAddress.addressLine2 || '',
            city: shippingAddress.city,
            emirate: shippingAddress.emirate,
            postalCode: shippingAddress.postalCode || '',
          },
        },
      });

      if (!orderResult.data.createRetailOrder.success) {
        throw new Error(orderResult.data.createRetailOrder.message);
      }

      const order = orderResult.data.createRetailOrder.order;

      // Step 2: Create Payment Session
      const paymentResult = await createPayment({
        variables: {
          input: {
            orderId: order.orderNumber,
            amount: order.totalAmount.toString(),
            currency: 'AED',
            customerEmail: customerInfo.email,
            customerPhone: customerInfo.phone,
            customerName: customerInfo.name,
            taxAmount: order.taxAmount?.toString() || '0.00',
            shippingAmount: order.deliveryFee?.toString() || '0.00',
            discountAmount: '0.00',
            items: order.items.map((item) => ({
              name: item.productName,
              price: item.unitPrice.toString(),
              quantity: item.quantity,
              sku: item.productSku || '',
            })),
            shippingAddress: {
              fullName: shippingAddress.fullName,
              phoneNumber: shippingAddress.phoneNumber,
              email: shippingAddress.email,
              addressLine1: shippingAddress.addressLine1,
              addressLine2: shippingAddress.addressLine2 || '',
              city: shippingAddress.city,
              emirate: shippingAddress.emirate,
              postalCode: shippingAddress.postalCode || '',
            },
          },
          gatewayName: 'ZIINA',
        },
      });

      if (!paymentResult.data.createPaymentSession.success) {
        throw new Error(paymentResult.data.createPaymentSession.message);
      }

      const payment = paymentResult.data.createPaymentSession;

      // Step 3: Save payment info and redirect
      localStorage.setItem('payment_id', payment.paymentId);
      localStorage.setItem('order_number', order.orderNumber);

      // Redirect to Ziina payment page
      window.location.href = payment.paymentUrl;

      return { success: true, paymentId: payment.paymentId };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  return { processPayment, loading, error };
}

// components/CheckoutForm.jsx
import { useState } from 'react';
import { usePayment } from '../hooks/usePayment';

export default function CheckoutForm({ cart, sessionKey }) {
  const { processPayment, loading, error } = usePayment();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    addressLine1: '',
    city: '',
    emirate: 'DUBAI',
    postalCode: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const result = await processPayment(
      { sessionKey },
      {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
      },
      {
        fullName: formData.name,
        phoneNumber: formData.phone,
        email: formData.email,
        addressLine1: formData.addressLine1,
        city: formData.city,
        emirate: formData.emirate,
        postalCode: formData.postalCode,
      }
    );

    if (!result.success) {
      alert(`Error: ${result.error}`);
    }
    // If successful, user will be redirected to payment page
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Full Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      <input
        type="tel"
        placeholder="Phone (+971501234567)"
        value={formData.phone}
        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
        required
      />
      <input
        type="text"
        placeholder="Address Line 1"
        value={formData.addressLine1}
        onChange={(e) => setFormData({ ...formData, addressLine1: e.target.value })}
        required
      />
      <input
        type="text"
        placeholder="City"
        value={formData.city}
        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
        required
      />
      <select
        value={formData.emirate}
        onChange={(e) => setFormData({ ...formData, emirate: e.target.value })}
        required
      >
        <option value="DUBAI">Dubai</option>
        <option value="ABU_DHABI">Abu Dhabi</option>
        <option value="SHARJAH">Sharjah</option>
        <option value="AJMAN">Ajman</option>
        <option value="UMM_AL_QUWAIN">Umm Al Quwain</option>
        <option value="RAS_AL_KHAIMAH">Ras Al Khaimah</option>
        <option value="FUJAIRAH">Fujairah</option>
      </select>
      <input
        type="text"
        placeholder="Postal Code"
        value={formData.postalCode}
        onChange={(e) => setFormData({ ...formData, postalCode: e.target.value })}
      />
      
      {error && <div className="error">{error}</div>}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Proceed to Payment'}
      </button>
    </form>
  );
}

// pages/payment/success.jsx (Next.js) or PaymentSuccess.jsx (React)
import { useEffect, useState } from 'react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import { useRouter } from 'next/router';

const GET_PAYMENT = gql`
  query GetPayment($paymentId: String!) {
    payment(paymentId: $paymentId) {
      id
      paymentId
      status
      amount
      order {
        orderNumber
        status
        customerName
        totalAmount
      }
    }
  }
`;

export default function PaymentSuccess() {
  const router = useRouter();
  const { payment_id } = router.query;
  const [paymentId, setPaymentId] = useState(null);

  useEffect(() => {
    // Get payment ID from URL or localStorage
    const urlPaymentId = router.query.payment_id;
    const storedPaymentId = localStorage.getItem('payment_id');
    const id = urlPaymentId || storedPaymentId;
    
    if (id) {
      setPaymentId(id);
    }
  }, [router.query]);

  const { data, loading, error } = useQuery(GET_PAYMENT, {
    variables: { paymentId },
    skip: !paymentId,
    pollInterval: 2000, // Poll every 2 seconds until payment is confirmed
  });

  if (loading) {
    return <div>Verifying payment...</div>;
  }

  if (error) {
    return <div>Error verifying payment: {error.message}</div>;
  }

  const payment = data?.payment;

  if (!payment) {
    return <div>Payment not found</div>;
  }

  // Check payment status
  if (payment.status === 'COMPLETED' || payment.status === 'CAPTURED') {
    // Payment successful
    return (
      <div className="success-page">
        <h1>✅ Payment Successful!</h1>
        <p>Thank you for your order, {payment.order.customerName}!</p>
        <p>Order Number: {payment.order.orderNumber}</p>
        <p>Amount Paid: AED {payment.amount}</p>
        <p>Your order is being processed and will be shipped soon.</p>
        <button onClick={() => router.push('/')}>Continue Shopping</button>
      </div>
    );
  }

  if (payment.status === 'FAILED') {
    return (
      <div className="error-page">
        <h1>❌ Payment Failed</h1>
        <p>Your payment could not be processed. Please try again.</p>
        <button onClick={() => router.push('/checkout')}>Try Again</button>
      </div>
    );
  }

  if (payment.status === 'PENDING') {
    return (
      <div>
        <h1>⏳ Payment Processing</h1>
        <p>Your payment is being processed. Please wait...</p>
      </div>
    );
  }

  return <div>Unknown payment status: {payment.status}</div>;
}
```

---

## 🚨 Error Handling

### Common Errors and Solutions

**1. Order Creation Failed**
```javascript
if (!orderResult.data.createRetailOrder.success) {
  const error = orderResult.data.createRetailOrder.message;
  // Handle error: "Cart is empty", "Product out of stock", etc.
  showError(error);
  return;
}
```

**2. Payment Session Creation Failed**
```javascript
if (!paymentResult.data.createPaymentSession.success) {
  const error = paymentResult.data.createPaymentSession.message;
  // Handle error: "Order not found", "Invalid amount", etc.
  showError(error);
  return;
}
```

**3. Network Errors**
```javascript
try {
  const result = await createPayment({...});
} catch (error) {
  if (error.networkError) {
    showError('Network error. Please check your connection.');
  } else {
    showError('An error occurred. Please try again.');
  }
}
```

**4. Payment Verification Failed**
```javascript
if (!payment) {
  // Payment not found - might be invalid payment_id
  showError('Payment not found. Please contact support.');
  return;
}
```

---

## 🧪 Testing

### Test Mode

Your backend should have `ZIINA_TEST_MODE=True` for testing.

### Test Card (Ziina Sandbox)

- **Card Number:** `4242 4242 4242 4242`
- **Expiry:** Any future date (e.g., `12/25`)
- **CVV:** Any 3 digits (e.g., `123`)
- **Name:** Any name

### Test Flow

1. Add items to cart
2. Fill checkout form
3. Click "Proceed to Payment"
4. Should redirect to Ziina payment page
5. Enter test card details
6. Complete payment
7. Should redirect back to success page
8. Payment status should be verified automatically

---

## 📋 Checklist

Before going live:

- [ ] GraphQL client configured
- [ ] Order creation working
- [ ] Payment session creation working
- [ ] Redirect to Ziina working
- [ ] Success page created
- [ ] Payment verification implemented
- [ ] Error handling in place
- [ ] Loading states shown
- [ ] Test payment successful
- [ ] Webhook URL configured in Ziina dashboard
- [ ] Production Ziina credentials configured

---

## 🔗 Important URLs

- **GraphQL Endpoint:** `http://164.90.215.173/graphql/`
- **Webhook URL:** `http://164.90.215.173/api/payments/webhooks/ziina/`
- **Success URL:** `{YOUR_FRONTEND_URL}/payment/success`
- **Cancel URL:** `{YOUR_FRONTEND_URL}/payment/cancel`
- **Failure URL:** `{YOUR_FRONTEND_URL}/payment/failure`

---

## 📝 Field Reference

### Payment Status Values

- `PENDING` - Payment is being processed
- `COMPLETED` - Payment successful
- `CAPTURED` - Payment captured
- `FAILED` - Payment failed
- `CANCELLED` - Payment cancelled
- `REFUNDED` - Payment refunded

### Order Status Values

- `PENDING` - Order created, awaiting payment
- `CONFIRMED` - Payment confirmed
- `PROCESSING` - Order being prepared
- `SHIPPED` - Order dispatched
- `DELIVERED` - Order delivered
- `CANCELLED` - Order cancelled

---

## 🎯 Quick Start

1. **Install dependencies:**
   ```bash
   npm install @apollo/client graphql
   ```

2. **Setup Apollo Client** (see GraphQL Setup section)

3. **Create checkout form** (see Code Examples)

4. **Create payment success page** (see Code Examples)

5. **Test with test card**

6. **Deploy!**

---

**Ready to integrate!** 🚀

Start with the checkout form, then add payment processing. The webhook will automatically update order status when payment succeeds.

