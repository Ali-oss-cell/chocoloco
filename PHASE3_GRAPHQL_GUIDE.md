# 🚀 Phase 3: GraphQL API Development

**Skip Phase 2 (Manual Admin Setup)** - Let's build the API first!

You can add products later through the admin or via the API itself.

---

## 📋 **What We're Building**

A complete GraphQL API for your chocolate e-commerce platform:

### **Public Queries** (No Authentication)
- Browse products
- View categories & brands
- Search & filter products
- View product details
- Check cart

### **Public Mutations** (No Authentication)
- Add to cart
- Update cart
- Remove from cart
- Checkout (retail)
- Initiate payment

### **Admin Mutations** (Will add later)
- Manage products
- Update inventory
- Process orders

---

## 🏗️ **Implementation Steps**

### **Step 1: Create Main GraphQL Schema**

Create: `ecomarce_choco/schema.py`

```python
import graphene
from products.schema import ProductQuery
from orders.schema import OrderQuery, OrderMutation
# Future: from users.schema import UserQuery, UserMutation

class Query(
    ProductQuery,
    OrderQuery,
    graphene.ObjectType
):
    """Root Query - combines all queries"""
    pass

class Mutation(
    OrderMutation,
    graphene.ObjectType
):
    """Root Mutation - combines all mutations"""
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

---

### **Step 2: Products Schema**

Create: `products/schema.py`

```python
import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from .models import Product, Category, Brand, ProductImage, ProductPrice, Inventory

# Types
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = '__all__'

class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = '__all__'

class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductPriceType(DjangoObjectType):
    effective_price = graphene.Decimal()
    
    class Meta:
        model = ProductPrice
        fields = '__all__'
    
    def resolve_effective_price(self, info):
        return self.get_effective_price()

class InventoryType(DjangoObjectType):
    available_quantity = graphene.Int()
    is_in_stock = graphene.Boolean()
    is_low_stock = graphene.Boolean()
    
    class Meta:
        model = Inventory
        fields = '__all__'
    
    def resolve_available_quantity(self, info):
        return self.available_quantity
    
    def resolve_is_in_stock(self, info):
        return self.is_in_stock
    
    def resolve_is_low_stock(self, info):
        return self.is_low_stock

class ProductType(DjangoObjectType):
    images = graphene.List(ProductImageType)
    prices = graphene.List(ProductPriceType)
    inventory = graphene.Field(InventoryType)
    retail_price = graphene.Decimal()
    in_stock = graphene.Boolean()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def resolve_images(self, info):
        return self.images.all()
    
    def resolve_prices(self, info):
        return self.prices.filter(is_active=True)
    
    def resolve_inventory(self, info):
        return self.inventory
    
    def resolve_retail_price(self, info):
        """Get retail price"""
        price = self.prices.filter(price_type='RETAIL', is_active=True).first()
        return price.get_effective_price() if price else None
    
    def resolve_in_stock(self, info):
        return self.inventory.is_in_stock if hasattr(self, 'inventory') else False

# Queries
class ProductQuery(graphene.ObjectType):
    # Single product
    product = graphene.Field(ProductType, id=graphene.Int(), slug=graphene.String())
    
    # List of products with filters
    products = graphene.List(
        ProductType,
        category=graphene.String(),
        brand=graphene.String(),
        search=graphene.String(),
        in_stock=graphene.Boolean(),
        featured=graphene.Boolean(),
    )
    
    # Categories
    categories = graphene.List(CategoryType, parent_id=graphene.Int())
    category = graphene.Field(CategoryType, id=graphene.Int(), slug=graphene.String())
    
    # Brands
    brands = graphene.List(BrandType, is_active=graphene.Boolean())
    brand = graphene.Field(BrandType, id=graphene.Int(), slug=graphene.String())
    
    def resolve_product(self, info, id=None, slug=None):
        if id:
            return Product.objects.filter(id=id, is_active=True).first()
        if slug:
            return Product.objects.filter(slug=slug, is_active=True).first()
        return None
    
    def resolve_products(self, info, category=None, brand=None, search=None, 
                        in_stock=None, featured=None):
        queryset = Product.objects.filter(is_active=True)
        
        if category:
            queryset = queryset.filter(category__slug=category)
        
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(sku__icontains=search)
            )
        
        if in_stock is not None:
            if in_stock:
                queryset = queryset.filter(inventory__quantity_in_stock__gt=0)
        
        if featured is not None:
            queryset = queryset.filter(featured=featured)
        
        return queryset.select_related('brand', 'category', 'inventory')
    
    def resolve_categories(self, info, parent_id=None):
        if parent_id:
            return Category.objects.filter(parent_category_id=parent_id, is_active=True)
        return Category.objects.filter(is_active=True)
    
    def resolve_category(self, info, id=None, slug=None):
        if id:
            return Category.objects.filter(id=id, is_active=True).first()
        if slug:
            return Category.objects.filter(slug=slug, is_active=True).first()
        return None
    
    def resolve_brands(self, info, is_active=None):
        queryset = Brand.objects.all()
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset
    
    def resolve_brand(self, info, id=None, slug=None):
        if id:
            return Brand.objects.filter(id=id, is_active=True).first()
        if slug:
            return Brand.objects.filter(slug=slug, is_active=True).first()
        return None
```

---

### **Step 3: Orders Schema**

Create: `orders/schema.py`

```python
import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from datetime import timedelta
import uuid
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, ShippingAddress
from products.models import Product

# Types
class CartItemType(DjangoObjectType):
    subtotal = graphene.Decimal()
    
    class Meta:
        model = CartItem
        fields = '__all__'
    
    def resolve_subtotal(self, info):
        return self.subtotal

class CartType(DjangoObjectType):
    items = graphene.List(CartItemType)
    total = graphene.Decimal()
    item_count = graphene.Int()
    
    class Meta:
        model = Cart
        fields = '__all__'
    
    def resolve_items(self, info):
        return self.items.all()
    
    def resolve_total(self, info):
        return sum(item.subtotal for item in self.items.all())
    
    def resolve_item_count(self, info):
        return sum(item.quantity for item in self.items.all())

class ShippingAddressType(DjangoObjectType):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderType(DjangoObjectType):
    items = graphene.List(OrderItemType)
    shipping_address = graphene.Field(ShippingAddressType)
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def resolve_items(self, info):
        return self.items.all()
    
    def resolve_shipping_address(self, info):
        return self.shipping_address

# Queries
class OrderQuery(graphene.ObjectType):
    cart = graphene.Field(CartType, session_key=graphene.String(required=True))
    order = graphene.Field(OrderType, order_number=graphene.String(required=True))
    
    def resolve_cart(self, info, session_key):
        return Cart.objects.filter(session_key=session_key).first()
    
    def resolve_order(self, info, order_number):
        return Order.objects.filter(order_number=order_number).first()

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=True)

class AddressInput(graphene.InputObjectType):
    full_name = graphene.String(required=True)
    phone_number = graphene.String(required=True)
    email = graphene.String(required=True)
    address_line1 = graphene.String(required=True)
    address_line2 = graphene.String()
    city = graphene.String(required=True)
    emirate = graphene.String(required=True)
    area = graphene.String()
    delivery_instructions = graphene.String()

# Mutations
class AddToCart(graphene.Mutation):
    class Arguments:
        session_key = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, session_key, product_id, quantity):
        try:
            # Get or create cart
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                defaults={'expires_at': timezone.now() + timedelta(days=2)}
            )
            
            # Get product
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Check inventory
            if not product.inventory.is_in_stock:
                return AddToCart(success=False, message="Product out of stock")
            
            if product.inventory.available_quantity < quantity:
                return AddToCart(
                    success=False, 
                    message=f"Only {product.inventory.available_quantity} items available"
                )
            
            # Get current retail price
            price = product.prices.filter(price_type='RETAIL', is_active=True).first()
            if not price:
                return AddToCart(success=False, message="Price not available")
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price_at_addition': price.get_effective_price()
                }
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return AddToCart(cart_item=cart_item, success=True, message="Added to cart")
            
        except Product.DoesNotExist:
            return AddToCart(success=False, message="Product not found")
        except Exception as e:
            return AddToCart(success=False, message=str(e))

class UpdateCartItem(graphene.Mutation):
    class Arguments:
        cart_item_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)
    
    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, cart_item_id, quantity):
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            
            if quantity <= 0:
                cart_item.delete()
                return UpdateCartItem(success=True, message="Item removed from cart")
            
            # Check inventory
            if cart_item.product.inventory.available_quantity < quantity:
                return UpdateCartItem(
                    success=False,
                    message=f"Only {cart_item.product.inventory.available_quantity} items available"
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return UpdateCartItem(cart_item=cart_item, success=True, message="Cart updated")
            
        except CartItem.DoesNotExist:
            return UpdateCartItem(success=False, message="Cart item not found")
        except Exception as e:
            return UpdateCartItem(success=False, message=str(e))

class RemoveFromCart(graphene.Mutation):
    class Arguments:
        cart_item_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, cart_item_id):
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            cart_item.delete()
            return RemoveFromCart(success=True, message="Item removed from cart")
        except CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Cart item not found")

class CreateRetailOrder(graphene.Mutation):
    class Arguments:
        session_key = graphene.String(required=True)
        customer_info = CustomerInput(required=True)
        shipping_address = AddressInput(required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, session_key, customer_info, shipping_address):
        try:
            # Get cart
            cart = Cart.objects.get(session_key=session_key)
            
            if not cart.items.exists():
                return CreateRetailOrder(success=False, message="Cart is empty")
            
            # Calculate totals
            subtotal = sum(item.subtotal for item in cart.items.all())
            vat_rate = Decimal('0.05')  # 5% VAT in UAE
            tax_amount = subtotal * vat_rate
            delivery_fee = Decimal('15.00')  # Default delivery fee
            total_amount = subtotal + tax_amount + delivery_fee
            
            # Create order
            order = Order.objects.create(
                order_type='RETAIL',
                status='PENDING',
                customer_name=customer_info.name,
                customer_email=customer_info.email,
                customer_phone=customer_info.phone,
                subtotal=subtotal,
                tax_amount=tax_amount,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                currency='AED'
            )
            
            # Create order items (snapshot product data)
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price_at_addition,
                    tax_amount=cart_item.price_at_addition * cart_item.quantity * vat_rate,
                    total_price=cart_item.price_at_addition * cart_item.quantity
                )
                
                # Reserve inventory
                inventory = cart_item.product.inventory
                inventory.reserved_quantity += cart_item.quantity
                inventory.save()
            
            # Create shipping address
            ShippingAddress.objects.create(
                order=order,
                full_name=shipping_address.full_name,
                phone_number=shipping_address.phone_number,
                email=shipping_address.email,
                address_line1=shipping_address.address_line1,
                address_line2=shipping_address.get('address_line2', ''),
                city=shipping_address.city,
                emirate=shipping_address.emirate,
                area=shipping_address.get('area', ''),
                delivery_instructions=shipping_address.get('delivery_instructions', '')
            )
            
            # Clear cart
            cart.items.all().delete()
            
            return CreateRetailOrder(
                order=order,
                success=True,
                message=f"Order created: {order.order_number}"
            )
            
        except Cart.DoesNotExist:
            return CreateRetailOrder(success=False, message="Cart not found")
        except Exception as e:
            return CreateRetailOrder(success=False, message=str(e))

# Mutation class
class OrderMutation(graphene.ObjectType):
    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_from_cart = RemoveFromCart.Field()
    create_retail_order = CreateRetailOrder.Field()
```

---

### **Step 4: Update URLs**

Update: `ecomarce_choco/urls.py`

```python
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🧪 **Testing Your API**

### **1. Access GraphiQL Interface**

Open browser: **http://localhost:8000/graphql**

You'll see an interactive API explorer!

### **2. Example Queries**

#### Get All Products:
```graphql
query {
  products {
    id
    name
    sku
    retailPrice
    inStock
    brand {
      name
    }
    category {
      name
    }
  }
}
```

#### Get Product by ID:
```graphql
query {
  product(id: 1) {
    name
    description
    retailPrice
    images {
      image
      isPrimary
    }
    inventory {
      availableQuantity
      isInStock
    }
  }
}
```

#### Get Categories:
```graphql
query {
  categories {
    id
    name
    slug
  }
}
```

### **3. Example Mutations**

#### Add to Cart:
```graphql
mutation {
  addToCart(
    sessionKey: "test-session-123"
    productId: 1
    quantity: 2
  ) {
    success
    message
    cartItem {
      id
      quantity
      subtotal
      product {
        name
      }
    }
  }
}
```

#### View Cart:
```graphql
query {
  cart(sessionKey: "test-session-123") {
    items {
      product {
        name
      }
      quantity
      subtotal
    }
    total
    itemCount
  }
}
```

#### Create Order:
```graphql
mutation {
  createRetailOrder(
    sessionKey: "test-session-123"
    customerInfo: {
      name: "John Doe"
      email: "john@example.com"
      phone: "+971501234567"
    }
    shippingAddress: {
      fullName: "John Doe"
      phoneNumber: "+971501234567"
      email: "john@example.com"
      addressLine1: "123 Main Street"
      city: "Dubai"
      emirate: "DUBAI"
    }
  ) {
    success
    message
    order {
      orderNumber
      totalAmount
      status
    }
  }
}
```

---

## ✅ **Implementation Checklist**

- [ ] Create `ecomarce_choco/schema.py`
- [ ] Create `products/schema.py`
- [ ] Create `orders/schema.py`
- [ ] Update `ecomarce_choco/urls.py`
- [ ] Restart server
- [ ] Test GraphiQL at http://localhost:8000/graphql
- [ ] Test product queries
- [ ] Test cart mutations
- [ ] Test order creation

---

## 🚀 **Quick Start Commands**

```bash
# Make sure server is stopped (Ctrl+C if running)

# Create the schema files (I'll help you with this)

# Restart server
source venv/bin/activate
python manage.py runserver

# Test API
# Open http://localhost:8000/graphql
```

---

## 📝 **Next Steps After API**

Once GraphQL is working:

1. **Add test products** via Django admin (quick!)
2. **Test complete checkout flow** via GraphiQL
3. **Integrate payment gateways** (Tabby, Tamara, Network)
4. **Connect React frontend** to your API
5. **Deploy and launch!**

---

Ready to implement? Let me know and I'll create all the schema files for you! 🚀

