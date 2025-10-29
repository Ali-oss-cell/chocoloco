# 📊 GraphQL Schema Summary

Quick reference of what your API can do right now.

---

## 🔍 QUERIES (Read Data)

### Products
| Query | Purpose | Example Use |
|-------|---------|-------------|
| `products` | Get all products | Homepage product listing |
| `product(id)` | Get single product | Product detail page |
| `categories` | Get all categories | Navigation menu |
| `category(id)` | Get single category | Category page |
| `brands` | Get all brands | Brand filter |
| `brand(id)` | Get single brand | Brand page |
| **`searchProducts(query)`** | **Search with autocomplete** | **Search bar** |

### Orders & Cart
| Query | Purpose | Example Use |
|-------|---------|-------------|
| `cart(sessionId)` | Get user's cart | Shopping cart page |
| `order(id)` | Get single order | Order details |
| `orders(userId)` | Get user's orders | Order history |

### Authentication
| Query | Purpose | Example Use |
|-------|---------|-------------|
| `verifyToken` | Check if token valid | Auth middleware |

---

## ✏️ MUTATIONS (Write Data)

### 👥 CUSTOMER Actions (No Login Required)

#### Shopping Cart
| Mutation | What It Does |
|----------|--------------|
| `addToCart` | Add product to cart |
| `updateCartItem` | Change quantity |
| `removeFromCart` | Remove item |
| `clearCart` | Empty cart |

#### Checkout
| Mutation | What It Does |
|----------|--------------|
| `createRetailOrder` | Place order (retail customer) |

### 🔧 ADMIN Actions (For Your Dashboard)

#### Categories
| Mutation | What It Does |
|----------|--------------|
| `createCategory` | Add new category |
| `updateCategory` | Edit category |

#### Brands
| Mutation | What It Does |
|----------|--------------|
| `createBrand` | Add new brand |
| `updateBrand` | Edit brand |

#### Products
| Mutation | What It Does |
|----------|--------------|
| `createProduct` | Add new product |
| `updateProduct` | Edit product |
| `deleteProduct` | Remove/deactivate product |
| `setProductPrice` | Set retail/wholesale price |
| `updateInventory` | Update stock levels |

#### Orders
| Mutation | What It Does |
|----------|--------------|
| `updateOrderStatus` | Change order status |
| `cancelOrder` | Cancel order + return stock |
| `updateShippingAddress` | Edit delivery address |

#### Authentication
| Mutation | What It Does |
|----------|--------------|
| `tokenAuth` | Login (get JWT token) |
| `refreshToken` | Refresh expired token |

---

## 🎯 What You Can Build Right Now

### ✅ Retail E-commerce Store (Phase 1)
- ✅ Product catalog with categories & brands
- ✅ Search with autocomplete
- ✅ Shopping cart (no login)
- ✅ Guest checkout
- ✅ Order management
- ✅ Inventory tracking

### 🔜 Coming Later (Phase 2)
- ⏳ Wholesale customer accounts
- ⏳ Wholesale special pricing
- ⏳ Payment gateway integration
- ⏳ Email notifications
- ⏳ Product reviews

---

## 📦 Data You Can Manage

### Products
```
Category → Brand → Product → Price + Inventory
```

### Orders
```
Cart → Order → OrderItems + Shipping Address
```

### Payments (Models ready, integration pending)
```
Order → Payment → PaymentGateway (Tabby/Tamara/Network)
```

---

## 🚀 Quick Example: Complete Flow

### Frontend (Customer)
```
1. Search products → searchProducts(query: "chocolate")
2. View product → product(id: 1)
3. Add to cart → addToCart(productId: 1, quantity: 2)
4. Checkout → createRetailOrder(...)
```

### Backend (You)
```
1. Create category → createCategory(name: "Chocolates")
2. Create brand → createBrand(name: "Lindt")
3. Create product → createProduct(...)
4. Set price → setProductPrice(...)
5. Add stock → updateInventory(...)
```

### Admin Dashboard (You)
```
1. View orders → orders(userId: null)  # All orders
2. Confirm order → updateOrderStatus(status: "CONFIRMED")
3. Ship order → updateOrderStatus(status: "SHIPPED")
4. Check stock → products { inventory { quantityInStock } }
```

---

## 🔑 Key Features

### 1. Search Engine
- Multi-field search (name, SKU, description, brand, category)
- Autocomplete support
- Relevance sorting (name matches first)
- Fast (limited to 10 results)

### 2. Inventory Management
- Real-time stock tracking
- Auto-deduct on order
- Auto-return on cancel
- Low stock alerts

### 3. Order Status Tracking
- 6 status levels (PENDING → DELIVERED)
- Status history log
- Notes for each change
- Cannot cancel delivered orders

### 4. Dual Pricing (Ready for Phase 2)
- RETAIL prices (for everyone)
- WHOLESALE prices (for bulk orders)
- Minimum quantity tiers

---

## 💻 How to Use

### GraphiQL Interface
```
http://localhost:8000/graphql/
```

### Example Query
```graphql
query {
  searchProducts(query: "chocolate", limit: 5) {
    id
    name
    brand { name }
    prices {
      basePrice
      salePrice
    }
    inventory {
      quantityInStock
      isInStock
    }
  }
}
```

### Example Mutation
```graphql
mutation {
  createProduct(input: {
    name: "Dark Chocolate"
    sku: "CHO-001"
    brandId: 1
    categoryId: 1
  }) {
    success
    message
    product { id name }
  }
}
```

---

## 📚 Full Documentation

- **Admin Guide**: See `ADMIN_API_GUIDE.md` for complete examples
- **Search Guide**: See `SEARCH_IMPLEMENTATION.md` for search details
- **Project Plan**: See `PROJECT_PLAN.md` for full feature list

---

## 🎉 Summary

**You have a fully functional e-commerce backend!**

✅ 22 mutations (10 customer + 12 admin)  
✅ 11 queries (read operations)  
✅ Search with autocomplete  
✅ Complete order management  
✅ Inventory tracking  
✅ Ready for custom dashboard  

**Next Step:** Add your first products and start building the frontend! 🚀

