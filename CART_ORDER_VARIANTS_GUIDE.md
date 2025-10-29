# Cart & Order System with Variants - Complete Guide

## ✅ **SYSTEM UPDATED - VARIANTS FULLY SUPPORTED!**

Your cart and order system now fully supports product variants! Customers can add different variants to their cart, and orders will track which specific variant was purchased.

---

## What Changed

### **Cart System:**
- ✅ Cart items can now store variant information
- ✅ Same product with different variants = different cart items
- ✅ Variant options displayed in cart
- ✅ Prices pulled from variant (not main product)
- ✅ Stock checked against variant inventory

### **Order System:**
- ✅ Orders store variant information permanently
- ✅ Variant options snapshot (preserved even if variant deleted)
- ✅ Variant SKU used in order items
- ✅ Inventory reserved from correct variant

---

## How to Add Variants to Cart

### **For Products with Variants:**

**You MUST specify which variant to add:**

```graphql
mutation {
  addToCart(
    sessionKey: "customer_session_123"
    productId: 21                        # Coco Mass
    variantId: 1                        # White 500g variant
    quantity: 2
  ) {
    success
    message
    cartItem {
      displayName                       # "Coco Mass - White, 500g"
      variantOptionsDisplay             # "White, 500g"
      quantity
      priceAtAddition
      subtotal
    }
  }
}
```

### **For Regular Products (No Variants):**

**Don't specify variantId:**

```graphql
mutation {
  addToCart(
    sessionKey: "customer_session_123"
    productId: 1                         # Regular product
    quantity: 1
  ) {
    success
    message
  }
}
```

### **Error Handling:**

If you try to add a product with variants without specifying which one:

```graphql
mutation {
  addToCart(
    sessionKey: "customer_session_123"
    productId: 21                        # Has variants!
    quantity: 1                          # ❌ No variantId
  ) {
    success  # false
    message  # "This product has variants. Please specify which variant to add."
  }
}
```

---

## View Cart with Variants

```graphql
query {
  cart(sessionKey: "customer_session_123") {
    items {
      id
      productName                        # "Coco Mass"
      displayName                        # "Coco Mass - White, 500g"
      variantOptionsDisplay              # "White, 500g"
      quantity
      priceAtAddition
      subtotal
      
      # Full details
      product {
        id
        name
      }
      variant {
        id
        sku
        price
        isInStock
        availableQuantity
      }
    }
    
    subtotal
    taxAmount
    total
    itemCount
  }
}
```

**Response Example:**
```json
{
  "cart": {
    "items": [
      {
        "displayName": "Coco Mass - White, 500g",
        "variantOptionsDisplay": "White, 500g",
        "quantity": 2,
        "priceAtAddition": "25.00",
        "subtotal": "50.00",
        "variant": {
          "sku": "COCO-WHITE-500",
          "price": "25.00",
          "isInStock": true,
          "availableQuantity": 148
        }
      },
      {
        "displayName": "Coco Mass - Dark, 1000g",
        "variantOptionsDisplay": "Dark, 1000g",
        "quantity": 1,
        "priceAtAddition": "50.00",
        "subtotal": "50.00"
      }
    ],
    "subtotal": "100.00",
    "taxAmount": "5.00",
    "total": "105.00"
  }
}
```

---

## Create Order with Variants

**The checkout process is the same - variants are handled automatically:**

```graphql
mutation {
  createRetailOrder(
    sessionKey: "customer_session_123"
    customerInfo: {
      name: "Ahmed Al Maktoum"
      email: "ahmed@example.com"
      phone: "+971501234567"
    }
    shippingAddress: {
      fullName: "Ahmed Al Maktoum"
      phoneNumber: "+971501234567"
      email: "ahmed@example.com"
      addressLine1: "123 Sheikh Zayed Road"
      city: "Dubai"
      emirate: "DUBAI"
    }
  ) {
    success
    message
    order {
      orderNumber
      customerName
      
      items {
        productName                      # "Coco Mass - White, 500g"
        productSku                       # "COCO-WHITE-500" (variant SKU)
        variantOptions                   # {"Color": "White", "Weight": "500g"}
        quantity
        unitPrice
        totalPrice
        
        # References
        variant {
          id
          sku
        }
      }
      
      subtotal
      taxAmount
      deliveryFee
      totalAmount
    }
  }
}
```

**Response Example:**
```json
{
  "order": {
    "orderNumber": "ORD-6E82C264",
    "customerName": "Ahmed Al Maktoum",
    "items": [
      {
        "productName": "Coco Mass - White, 500g",
        "productSku": "COCO-WHITE-500",
        "variantOptions": {
          "Color": "White",
          "Weight": "500g"
        },
        "quantity": 2,
        "unitPrice": "25.00",
        "totalPrice": "50.00"
      },
      {
        "productName": "Coco Mass - Dark, 1000g",
        "productSku": "COCO-DARK-1000",
        "variantOptions": {
          "Color": "Dark",
          "Weight": "1000g"
        },
        "quantity": 1,
        "unitPrice": "50.00",
        "totalPrice": "50.00"
      }
    ],
    "subtotal": "100.00",
    "taxAmount": "5.00",
    "deliveryFee": "15.00",
    "totalAmount": "120.00"
  }
}
```

---

## View Order with Variants

```graphql
query {
  order(orderNumber: "ORD-6E82C264") {
    orderNumber
    customerName
    status
    
    items {
      productName
      productSku
      variantOptions                     # Preserved snapshot!
      quantity
      unitPrice
      totalPrice
    }
    
    totalAmount
  }
}
```

---

## Frontend Implementation

### **Product Page with Variants:**

```javascript
// When customer selects variant on product page:
function addToCart(product, selectedVariant, quantity) {
  const mutation = `
    mutation {
      addToCart(
        sessionKey: "${getSessionKey()}"
        productId: ${product.id}
        variantId: ${selectedVariant.id}
        quantity: ${quantity}
      ) {
        success
        message
        cart {
          itemCount
          total
        }
      }
    }
  `;
  
  // Execute mutation...
}

// Variant selector example:
<div className="variant-selector">
  <h4>Select Options:</h4>
  
  {/* Color selector */}
  <div className="option-group">
    <label>Color:</label>
    <div className="option-buttons">
      <button onClick={() => setColor('White')}>White</button>
      <button onClick={() => setColor('Dark')}>Dark</button>
    </div>
  </div>
  
  {/* Weight selector */}
  <div className="option-group">
    <label>Weight:</label>
    <div className="option-buttons">
      <button onClick={() => setWeight('500g')}>500g</button>
      <button onClick={() => setWeight('1kg')}>1kg</button>
    </div>
  </div>
  
  {/* Selected variant info */}
  <div className="selected-variant">
    <p>SKU: {selectedVariant.sku}</p>
    <p>Price: {selectedVariant.effectivePrice} AED</p>
    <p>Stock: {selectedVariant.availableQuantity} units</p>
  </div>
  
  <button onClick={() => addToCart(product, selectedVariant, 1)}>
    Add to Cart
  </button>
</div>
```

### **Cart Page:**

```javascript
// Display cart with variant information
function CartItem({ item }) {
  return (
    <div className="cart-item">
      <h4>{item.displayName}</h4>
      {item.variantOptionsDisplay && (
        <p className="variant-info">{item.variantOptionsDisplay}</p>
      )}
      <p>Price: {item.priceAtAddition} AED</p>
      <p>Quantity: {item.quantity}</p>
      <p>Subtotal: {item.subtotal} AED</p>
    </div>
  );
}
```

### **Order Confirmation:**

```javascript
// Display order with variant details
function OrderItem({ item }) {
  const variantInfo = item.variantOptions 
    ? Object.entries(item.variantOptions).map(([k, v]) => `${k}: ${v}`).join(', ')
    : null;
    
  return (
    <div className="order-item">
      <h4>{item.productName}</h4>
      {variantInfo && <p className="variant-info">({variantInfo})</p>}
      <p>SKU: {item.productSku}</p>
      <p>{item.quantity} x {item.unitPrice} AED = {item.totalPrice} AED</p>
    </div>
  );
}
```

---

## Key Features

### **✅ What Works:**

1. **Multiple Variants in Cart:**
   - Customer can add White 500g AND Dark 1kg to same cart
   - Each is a separate cart item
   - Each tracked independently

2. **Stock Management:**
   - Stock checked for specific variant
   - Inventory reserved from correct variant
   - Available quantity calculated per variant

3. **Pricing:**
   - Variant price used (not main product price)
   - Sale prices honored per variant
   - Price snapshot at time of adding to cart

4. **Order History:**
   - Variant information preserved permanently
   - Even if variant is deleted later
   - SKU shows which variant was ordered

5. **Display Names:**
   - Automatic "Product - Options" format
   - "Coco Mass - White, 500g"
   - "Food Coloring - Red, 100g"

---

## Testing Checklist

### **✅ All Tests Passed:**

- ✅ Add variant to cart
- ✅ Add multiple variants of same product
- ✅ Display variant options in cart
- ✅ Calculate prices from variant
- ✅ Check stock against variant
- ✅ Create order with variants
- ✅ Store variant info in order
- ✅ Reserve inventory from variant
- ✅ Use variant SKU in order
- ✅ Error when variant not specified
- ✅ Cart empties after order

---

## Database Schema

### **CartItem Table:**
```
id
cart_id                    (FK to Cart)
product_id                 (FK to Product)
variant_id                 (FK to ProductVariant, nullable)
quantity
price_at_addition
created_at
updated_at

UNIQUE (cart_id, product_id, variant_id)
```

### **OrderItem Table:**
```
id
order_id                   (FK to Order)
product_id                 (FK to Product)
variant_id                 (FK to ProductVariant, nullable)
product_name               (snapshot)
product_sku                (variant SKU if applicable)
variant_options            (JSON snapshot)
quantity
unit_price
tax_amount
total_price
created_at
```

---

## Migration Notes

### **✅ Migrations Applied:**

**orders/migrations/0002_...**
- Added `variant` field to CartItem
- Added `variant` field to OrderItem
- Added `variant_options` JSON field to OrderItem
- Updated unique constraint on CartItem to include variant

**No data loss** - Existing carts and orders continue to work!

---

## API Changes Summary

### **Updated Mutations:**

```graphql
# NEW: variantId parameter (optional)
addToCart(
  sessionKey: String!
  productId: Int!
  variantId: Int              # NEW - Required if product has variants
  quantity: Int!
)

# Unchanged - works automatically
createRetailOrder(
  sessionKey: String!
  customerInfo: CustomerInput!
  shippingAddress: AddressInput!
)
```

### **Updated Types:**

```graphql
type CartItemType {
  # Existing fields...
  variant: ProductVariantType        # NEW
  displayName: String                # NEW
  variantOptionsDisplay: String      # NEW
}

type OrderItemType {
  # Existing fields...
  variant: ProductVariantType        # NEW
  variantOptions: JSONString         # NEW
}
```

---

## Best Practices

### **1. Always Check for Variants:**

```javascript
// Before adding to cart
if (product.hasVariants && !selectedVariant) {
  alert('Please select product options');
  return;
}
```

### **2. Display Variant Info:**

```javascript
// In cart and order displays
const displayName = item.variantOptionsDisplay 
  ? `${item.productName} (${item.variantOptionsDisplay})`
  : item.productName;
```

### **3. Stock Validation:**

```javascript
// Check correct inventory
const stock = selectedVariant 
  ? selectedVariant.availableQuantity
  : product.inventory.availableQuantity;
  
if (quantity > stock) {
  alert(`Only ${stock} available`);
}
```

---

## Summary

### **✅ Complete Integration:**

- **Cart System:** Fully supports variants
- **Order System:** Tracks variants permanently
- **Inventory:** Reserves from correct variant
- **Pricing:** Uses variant-specific prices
- **Display:** Shows variant options clearly
- **API:** Backward compatible
- **Testing:** All scenarios validated

### **🎯 Ready for Production:**

Your cart and order system now handles both:
- Regular products (no variants)
- Variant products (with options)

Both work seamlessly in the same system!

**You can now sell variants and track them through the entire customer journey!** 🛒✨

