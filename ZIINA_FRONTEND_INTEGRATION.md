# Ziina Payment Frontend Integration Guide

Complete guide for integrating Ziina payments in your frontend application.

---

## 📋 Overview

Ziina is a UAE Central Bank licensed instant payment gateway that supports:
- Credit/Debit Cards
- Apple Pay
- Instant bank transfers
- Real-time payment processing

---

## 🔄 Payment Flow

### Step 1: Create Order
First, create an order using the `createRetailOrder` mutation (from cart).

### Step 2: Create Payment Session
Call `createPaymentSession` mutation with order details and `gatewayName: "ZIINA"`.

### Step 3: Redirect to Payment
Redirect user to the `paymentUrl` returned from the mutation.

### Step 4: Handle Callback
After payment, user is redirected to your success/cancel/failure URLs.

### Step 5: Verify Payment
Verify payment status using `verifyPayment` mutation.

---

## 🚀 GraphQL Mutations

### 1. Create Payment Session

**Mutation:**
```graphql
mutation CreateZiinaPayment($input: PaymentSessionInput!, $gatewayName: String!) {
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
    "orderId": "ORD-12345",
    "amount": "105.00",
    "currency": "AED",
    "customerEmail": "customer@example.com",
    "customerPhone": "+971501234567",
    "customerName": "John Doe",
    "taxAmount": "5.00",
    "shippingAmount": "0.00",
    "discountAmount": "0.00",
    "items": [
      {
        "name": "Premium Chocolate Box",
        "price": "100.00",
        "quantity": 1,
        "sku": "CHOC-001"
      }
    ],
    "shippingAddress": {
      "fullName": "John Doe",
      "phoneNumber": "+971501234567",
      "email": "customer@example.com",
      "addressLine1": "123 Main Street",
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
      "paymentId": "ZIINA_PAY_123456",
      "expiresAt": "2024-01-15T10:30:00Z",
      "gatewayResponse": {
        "id": "ZIINA_PAY_123456",
        "status": "pending",
        "amount": 10500,
        "currency": "AED"
      }
    }
  }
}
```

---

### 2. Verify Payment Status

**Mutation:**
```graphql
mutation VerifyZiinaPayment($input: PaymentVerificationInput!) {
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
    "paymentId": "ZIINA_PAY_123456",
    "gatewayName": "ZIINA"
  }
}
```

**Response:**
```json
{
  "data": {
    "verifyPayment": {
      "success": true,
      "message": "Payment verified successfully",
      "status": "completed",
      "amount": "105.00",
      "transactionId": "TXN_789012",
      "gatewayResponse": {
        "id": "ZIINA_PAY_123456",
        "status": "completed",
        "transaction_id": "TXN_789012"
      }
    }
  }
}
```

**Payment Status Values:**
- `pending` - Payment is being processed
- `completed` - Payment successful
- `failed` - Payment failed
- `cancelled` - Payment cancelled by user

---

## 💻 Frontend Implementation Examples

### React/Next.js Example

```javascript
import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { gql } from '@apollo/client';

const CREATE_PAYMENT_SESSION = gql`
  mutation CreateZiinaPayment($input: PaymentSessionInput!, $gatewayName: String!) {
    createPaymentSession(input: $input, gatewayName: $gatewayName) {
      success
      message
      paymentUrl
      paymentId
      expiresAt
    }
  }
`;

const VERIFY_PAYMENT = gql`
  mutation VerifyZiinaPayment($input: PaymentVerificationInput!) {
    verifyPayment(input: $input) {
      success
      status
      amount
      transactionId
    }
  }
`;

function PaymentButton({ order, customerInfo }) {
  const [createPayment, { loading }] = useMutation(CREATE_PAYMENT_SESSION);
  const [verifyPayment] = useMutation(VERIFY_PAYMENT);

  const handlePayment = async () => {
    try {
      // Step 1: Create payment session
      const { data } = await createPayment({
        variables: {
          input: {
            orderId: order.orderNumber,
            amount: order.total.toString(),
            currency: "AED",
            customerEmail: customerInfo.email,
            customerPhone: customerInfo.phone,
            customerName: customerInfo.name,
            taxAmount: order.taxAmount.toString(),
            shippingAmount: order.shippingAmount?.toString() || "0.00",
            items: order.items.map(item => ({
              name: item.productName,
              price: item.unitPrice.toString(),
              quantity: item.quantity,
              sku: item.productSku
            })),
            shippingAddress: {
              fullName: customerInfo.name,
              phoneNumber: customerInfo.phone,
              email: customerInfo.email,
              addressLine1: customerInfo.address.addressLine1,
              city: customerInfo.address.city,
              emirate: customerInfo.address.emirate,
              postalCode: customerInfo.address.postalCode
            }
          },
          gatewayName: "ZIINA"
        }
      });

      if (data.createPaymentSession.success) {
        // Step 2: Redirect to payment URL
        window.location.href = data.createPaymentSession.paymentUrl;
      } else {
        alert(`Payment error: ${data.createPaymentSession.message}`);
      }
    } catch (error) {
      console.error('Payment creation error:', error);
      alert('Failed to create payment session. Please try again.');
    }
  };

  return (
    <button 
      onClick={handlePayment} 
      disabled={loading}
      className="bg-blue-600 text-white px-6 py-3 rounded-lg"
    >
      {loading ? 'Processing...' : 'Pay with Ziina'}
    </button>
  );
}

// Handle payment callback (in success page)
export function PaymentSuccessPage() {
  const [verifyPayment, { loading }] = useMutation(VERIFY_PAYMENT);
  const [paymentStatus, setPaymentStatus] = useState(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const paymentId = urlParams.get('payment_id');

    if (paymentId) {
      verifyPaymentStatus(paymentId);
    }
  }, []);

  const verifyPaymentStatus = async (paymentId) => {
    try {
      const { data } = await verifyPayment({
        variables: {
          input: {
            paymentId: paymentId,
            gatewayName: "ZIINA"
          }
        }
      });

      if (data.verifyPayment.success) {
        setPaymentStatus(data.verifyPayment.status);
        
        if (data.verifyPayment.status === 'completed') {
          // Payment successful - update order status, show success message
          console.log('Payment successful!', data.verifyPayment);
        } else if (data.verifyPayment.status === 'failed') {
          // Payment failed - show error message
          console.log('Payment failed');
        }
      }
    } catch (error) {
      console.error('Payment verification error:', error);
    }
  };

  if (loading) {
    return <div>Verifying payment...</div>;
  }

  if (paymentStatus === 'completed') {
    return <div>Payment successful! Thank you for your order.</div>;
  }

  if (paymentStatus === 'failed') {
    return <div>Payment failed. Please try again.</div>;
  }

  return <div>Processing payment...</div>;
}
```

---

### Vue.js Example

```vue
<template>
  <div>
    <button 
      @click="initiatePayment" 
      :disabled="loading"
      class="payment-button"
    >
      {{ loading ? 'Processing...' : 'Pay with Ziina' }}
    </button>
  </div>
</template>

<script>
import { gql } from '@apollo/client/core';
import { useMutation } from '@vue/apollo-composable';

const CREATE_PAYMENT_SESSION = gql`
  mutation CreateZiinaPayment($input: PaymentSessionInput!, $gatewayName: String!) {
    createPaymentSession(input: $input, gatewayName: $gatewayName) {
      success
      message
      paymentUrl
      paymentId
    }
  }
`;

export default {
  name: 'ZiinaPayment',
  props: {
    order: Object,
    customerInfo: Object
  },
  setup(props) {
    const { mutate: createPayment, loading } = useMutation(CREATE_PAYMENT_SESSION);

    const initiatePayment = async () => {
      try {
        const { data } = await createPayment({
          input: {
            orderId: props.order.orderNumber,
            amount: props.order.total.toString(),
            currency: "AED",
            customerEmail: props.customerInfo.email,
            customerPhone: props.customerInfo.phone,
            customerName: props.customerInfo.name,
            // ... other fields
          },
          gatewayName: "ZIINA"
        });

        if (data.createPaymentSession.success) {
          window.location.href = data.createPaymentSession.paymentUrl;
        }
      } catch (error) {
        console.error('Payment error:', error);
      }
    };

    return {
      initiatePayment,
      loading
    };
  }
};
</script>
```

---

## 🔗 Payment Redirect URLs

After payment, Ziina redirects users to these URLs (configured in backend):

- **Success:** `{FRONTEND_URL}/payment/success?payment_id={payment_id}`
- **Cancel:** `{FRONTEND_URL}/payment/cancel?payment_id={payment_id}`
- **Failure:** `{FRONTEND_URL}/payment/failure?payment_id={payment_id}`

**Important:** Always verify payment status on the success page using the `verifyPayment` mutation. Don't trust URL parameters alone.

---

## ✅ Best Practices

### 1. Always Verify Payment
Never trust the redirect URL alone. Always call `verifyPayment` mutation to confirm payment status.

### 2. Handle Errors Gracefully
```javascript
try {
  const { data } = await createPayment({...});
  if (!data.createPaymentSession.success) {
    // Handle error
    showError(data.createPaymentSession.message);
  }
} catch (error) {
  // Handle network/GraphQL errors
  showError('Network error. Please try again.');
}
```

### 3. Store Payment ID
Store the `paymentId` in localStorage or sessionStorage so you can verify it later if needed.

### 4. Handle Expired Sessions
Check `expiresAt` before redirecting. If expired, create a new payment session.

### 5. Show Loading States
Always show loading indicators during payment creation and verification.

---

## 🧪 Testing

### Test Mode
Set `ZIINA_TEST_MODE=True` in backend `.env` for testing.

### Test Cards
Ziina will provide test card numbers in their sandbox environment.

### Test Flow
1. Create order
2. Create payment session with test amount
3. Use test card in Ziina payment page
4. Verify payment status

---

## 📱 Apple Pay Integration (Optional)

If you have `ZIINA_PUBLIC_KEY` configured, you can enable Apple Pay:

```javascript
// Get Apple Pay config
const GET_APPLE_PAY_CONFIG = gql`
  query {
    paymentGateways(isActive: true) {
      name
      config
    }
  }
`;

// Use Ziina's Apple Pay SDK (check Ziina documentation)
```

---

## 🔍 Query Payment Status

You can also query payment status without mutation:

```graphql
query GetPayment($paymentId: String!) {
  payment(paymentId: $paymentId) {
    id
    paymentId
    status
    amount
    currency
    gateway
    createdAt
    verifiedAt
    gatewayResponse
  }
}
```

---

## 🚨 Error Handling

### Common Errors

**1. Payment Session Creation Failed**
- Check if order exists
- Verify amount is correct
- Ensure customer info is complete

**2. Payment Verification Failed**
- Payment ID might be invalid
- Payment might not exist
- Network error

**3. Payment Expired**
- Check `expiresAt` timestamp
- Create new payment session

---

## 📞 Support

- **Ziina Documentation:** https://ziina.com/docs
- **Backend API:** Check `PAYMENT_GATEWAY_SETUP.md` for backend configuration
- **GraphQL Endpoint:** `http://your-backend-url/graphql/`

---

## 📝 Complete Payment Flow Diagram

```
User clicks "Pay"
    ↓
Frontend: createPaymentSession mutation
    ↓
Backend: Creates Ziina payment session
    ↓
Frontend: Receives paymentUrl
    ↓
Frontend: Redirects to paymentUrl
    ↓
User completes payment on Ziina
    ↓
Ziina redirects to success/cancel/failure URL
    ↓
Frontend: verifyPayment mutation
    ↓
Backend: Verifies with Ziina API
    ↓
Frontend: Updates UI based on status
```

---

## 🎯 Quick Start Checklist

- [ ] Backend has Ziina credentials configured
- [ ] Frontend has GraphQL client setup
- [ ] Payment redirect URLs are configured
- [ ] Success/cancel/failure pages are created
- [ ] Payment verification is implemented
- [ ] Error handling is in place
- [ ] Test mode is enabled for development

---

**Ready to integrate?** Start with the `createPaymentSession` mutation and redirect to the payment URL!

