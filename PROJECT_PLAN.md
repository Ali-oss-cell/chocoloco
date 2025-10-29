# 🍫 E-Commerce Chocolate Platform - Complete Project Plan

**Location**: UAE  
**Backend**: Django + GraphQL  
**Frontend**: React  
**Focus**: Backend Development  

---

## 📊 PROJECT OVERVIEW

### Business Requirements
- **Retail Customers**: No login required, can purchase small quantities (1kg, 1 bottle, etc.)
- **Wholesale Customers**: Accounts created by admin after offline paperwork, login with username/password, special pricing, bulk quantities
- **Products**: Organized by categories and brands
- **Payment Gateways**: Tabby, Tamara, Network International
- **Admin Dashboard**: Manage prices, products, orders, and wholesale customers

### Important Notes
- **Wholesale Onboarding**: Happens OFFLINE - customers complete paperwork in person, then admin creates their account
- **No Self-Registration**: Wholesale customers don't register themselves on the website
- **Simple Account Creation**: Admin just creates username/password and basic info after paperwork is complete

### Current State
✅ Django project initialized  
✅ Custom User model created  
✅ Apps created: users, products, orders, payments  
⚠️ Models need implementation  
⚠️ GraphQL needs setup  
⚠️ Payment gateways need integration  

---

## 🗂️ DATABASE MODELS ARCHITECTURE

### 1. USERS APP (`users/models.py`)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extended User Model for Staff and Wholesale Customers
    
    Note: Wholesale accounts are created by admin after completing offline paperwork.
    Admin creates username, password, and basic info - no self-registration needed.
    """
    USER_TYPE_CHOICES = [
        ('STAFF', 'Staff/Admin'),
        ('WHOLESALE', 'Wholesale Customer'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='WHOLESALE')
    phone_number = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True, help_text="Business name for wholesale customers")
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Credit limit in AED")
    is_active = models.BooleanField(default=True, help_text="Set to False to suspend account")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        
    def __str__(self):
        if self.company_name:
            return f"{self.username} ({self.company_name})"
        return self.username


class WholesaleProfile(models.Model):
    """Additional details for wholesale customers (created by admin after offline paperwork)"""
    PAYMENT_TERMS_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('NET30', 'Net 30 Days'),
        ('NET60', 'Net 60 Days'),
        ('PREPAID', 'Prepaid'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wholesale_profile')
    company_address = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='COD')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Special discount for this customer")
    minimum_order_quantity = models.IntegerField(default=1, help_text="Minimum order quantity in units")
    notes = models.TextField(blank=True, help_text="Internal notes about this customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wholesale_profiles'
        
    def __str__(self):
        return f"Wholesale Profile - {self.user.company_name}"
```

---

### 2. PRODUCTS APP (`products/models.py`)

```python
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """Product Categories with nested support"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Chocolate Brands"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Main Product Model"""
    UNIT_TYPE_CHOICES = [
        ('KG', 'Kilogram'),
        ('GRAM', 'Gram'),
        ('BOTTLE', 'Bottle'),
        ('PIECE', 'Piece'),
        ('BOX', 'Box'),
        ('PACK', 'Pack'),
    ]
    
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    ingredients = models.TextField(blank=True)
    allergen_info = models.TextField(blank=True)
    nutritional_info = models.JSONField(default=dict, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in grams", null=True, blank=True)
    volume = models.DecimalField(max_digits=10, decimal_places=2, help_text="Volume in ml", null=True, blank=True)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES, default='PIECE')
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductImage(models.Model):
    """Multiple images per product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        ordering = ['display_order']

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductPrice(models.Model):
    """Separate pricing for retail vs wholesale"""
    PRICE_TYPE_CHOICES = [
        ('RETAIL', 'Retail Price'),
        ('WHOLESALE', 'Wholesale Price'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price_type = models.CharField(max_length=20, choices=PRICE_TYPE_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='AED')
    min_quantity = models.IntegerField(default=1, help_text="Minimum quantity for this price tier")
    max_quantity = models.IntegerField(null=True, blank=True, help_text="Maximum quantity for this price tier")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_prices'
        ordering = ['price_type', 'min_quantity']
        unique_together = ['product', 'price_type', 'min_quantity']

    def __str__(self):
        return f"{self.product.name} - {self.price_type} - {self.base_price} {self.currency}"

    def get_effective_price(self):
        """Return sale price if available, otherwise base price"""
        return self.sale_price if self.sale_price else self.base_price


class Inventory(models.Model):
    """Stock management"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity_in_stock = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0, help_text="Quantity reserved for pending orders")
    low_stock_threshold = models.IntegerField(default=10)
    warehouse_location = models.CharField(max_length=255, blank=True)
    last_restocked_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'Inventory'

    @property
    def available_quantity(self):
        """Calculate available quantity (in stock - reserved)"""
        return self.quantity_in_stock - self.reserved_quantity

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.available_quantity > 0

    @property
    def is_low_stock(self):
        """Check if stock is below threshold"""
        return self.available_quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.product.name} - Stock: {self.available_quantity}"


class ProductReview(models.Model):
    """Customer reviews"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.name} by {self.customer_name}"
```

---

### 3. ORDERS APP (`orders/models.py`)

```python
from django.db import models
from django.conf import settings
import uuid

class Cart(models.Model):
    """Shopping cart for retail customers"""
    session_key = models.CharField(max_length=255, unique=True, help_text="Session key for retail customers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart {self.session_key}"


class CartItem(models.Model):
    """Items in cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price_at_addition * self.quantity


class Order(models.Model):
    """Main Order Model"""
    ORDER_TYPE_CHOICES = [
        ('RETAIL', 'Retail Order'),
        ('WHOLESALE', 'Wholesale Order'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Customer Information (for retail customers without login)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_company = models.CharField(max_length=255, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="VAT 5% in UAE")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='AED')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Additional
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Staff only notes")

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number"""
        prefix = 'ORD'
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"{prefix}-{unique_id}"

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, help_text="Snapshot of product name")
    product_sku = models.CharField(max_length=100, help_text="Snapshot of SKU")
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit at time of order")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class ShippingAddress(models.Model):
    """Delivery address"""
    EMIRATE_CHOICES = [
        ('DUBAI', 'Dubai'),
        ('ABU_DHABI', 'Abu Dhabi'),
        ('SHARJAH', 'Sharjah'),
        ('AJMAN', 'Ajman'),
        ('UMM_AL_QUWAIN', 'Umm Al Quwain'),
        ('RAS_AL_KHAIMAH', 'Ras Al Khaimah'),
        ('FUJAIRAH', 'Fujairah'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    emirate = models.CharField(max_length=50, choices=EMIRATE_CHOICES)
    area = models.CharField(max_length=100, blank=True, help_text="Area/District")
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='UAE')
    delivery_instructions = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipping_addresses'

    def __str__(self):
        return f"{self.full_name} - {self.emirate}"


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_history'
        ordering = ['-created_at']
        verbose_name_plural = 'Order Status Histories'

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
```

---

### 4. PAYMENTS APP (`payments/models.py`)

```python
from django.db import models
from django.conf import settings
import uuid

class PaymentGateway(models.Model):
    """Payment gateway configuration"""
    GATEWAY_CHOICES = [
        ('TABBY', 'Tabby'),
        ('TAMARA', 'Tamara'),
        ('NETWORK', 'Network International'),
    ]
    
    name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    api_key = models.CharField(max_length=255, help_text="Encrypted API key")
    api_secret = models.CharField(max_length=255, help_text="Encrypted API secret")
    webhook_url = models.URLField(blank=True)
    supported_currencies = models.JSONField(default=list)
    config = models.JSONField(default=dict, help_text="Gateway-specific configuration")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_gateways'

    def __str__(self):
        return self.display_name


class Payment(models.Model):
    """Payment transactions"""
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('INSTALLMENTS', 'Installments'),
        ('COD', 'Cash on Delivery'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('AUTHORIZED', 'Authorized'),
        ('CAPTURED', 'Captured'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    payment_id = models.CharField(max_length=100, unique=True, editable=False)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='AED')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Gateway Details
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict)
    
    # Installments (for Tabby/Tamara)
    is_installment = models.BooleanField(default=False)
    installment_count = models.IntegerField(null=True, blank=True)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Additional
    failure_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        super().save(*args, **kwargs)

    def generate_payment_id(self):
        """Generate unique payment ID"""
        prefix = 'PAY'
        unique_id = uuid.uuid4().hex[:12].upper()
        return f"{prefix}-{unique_id}"

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"


class Refund(models.Model):
    """Refund transactions"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    refund_id = models.CharField(max_length=100, unique=True, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    gateway_refund_id = models.CharField(max_length=255, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'refunds'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = self.generate_refund_id()
        super().save(*args, **kwargs)

    def generate_refund_id(self):
        """Generate unique refund ID"""
        prefix = 'REF'
        unique_id = uuid.uuid4().hex[:10].upper()
        return f"{prefix}-{unique_id}"

    def __str__(self):
        return f"Refund {self.refund_id}"


class PaymentWebhook(models.Model):
    """Log webhooks from payment gateways"""
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
    ]
    
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    webhook_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_webhooks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook {self.webhook_type} - {self.status}"
```

---

## 📝 PHASE-BY-PHASE TODO LIST

### ✅ PHASE 1: Foundation Setup (Week 1-2)

#### A. Install Required Packages
```bash
# Core dependencies
- [ ] pip install graphene-django
- [ ] pip install django-graphql-jwt
- [ ] pip install django-cors-headers
- [ ] pip install pillow
- [ ] pip install django-filter
- [ ] pip install python-decouple
- [ ] pip install celery redis
- [ ] pip install django-storages boto3  # Optional for S3
- [ ] pip freeze > requirements.txt
```

#### B. Update settings.py
```python
- [ ] Add 'graphene_django' to INSTALLED_APPS
- [ ] Add 'corsheaders' to INSTALLED_APPS
- [ ] Add CORS middleware
- [ ] Set TIME_ZONE = 'Asia/Dubai'
- [ ] Configure MEDIA_URL and MEDIA_ROOT
- [ ] Add GRAPHENE settings
- [ ] Move SECRET_KEY to .env file
- [ ] Configure ALLOWED_HOSTS
```

#### C. Environment Setup
- [ ] Create .env file in project root
- [ ] Add SECRET_KEY to .env
- [ ] Add DATABASE_URL to .env (for production)
- [ ] Add payment gateway credentials to .env
- [ ] Update .gitignore to exclude .env

#### D. GraphQL Setup
- [ ] Create schema.py in main project folder
- [ ] Add GraphQL URL to urls.py
- [ ] Test GraphiQL interface

---

### ✅ PHASE 2: Implement Models (Week 2-3)

#### A. Users App Models
- [ ] Update User model in users/models.py (simplified - no approval workflow)
- [ ] Create WholesaleProfile model (simple fields only)
- [ ] Create admin.py for user management (focus on easy account creation)
- [ ] Create signals.py for auto-profile creation when wholesale user is created
- [ ] Run makemigrations for users app
- [ ] Run migrate for users app

Note: Keep it simple! Admin creates wholesale accounts after offline paperwork is complete.

#### B. Products App Models
- [ ] Implement Category model
- [ ] Implement Brand model
- [ ] Implement Product model
- [ ] Implement ProductImage model
- [ ] Implement ProductPrice model
- [ ] Implement Inventory model
- [ ] Implement ProductReview model
- [ ] Create admin.py with inline editing
- [ ] Run makemigrations for products app
- [ ] Run migrate for products app

#### C. Orders App Models
- [ ] Implement Cart model
- [ ] Implement CartItem model
- [ ] Implement Order model
- [ ] Implement OrderItem model
- [ ] Implement ShippingAddress model
- [ ] Implement OrderStatusHistory model
- [ ] Create admin.py for order management
- [ ] Run makemigrations for orders app
- [ ] Run migrate for orders app

#### D. Payments App Models
- [ ] Implement PaymentGateway model
- [ ] Implement Payment model
- [ ] Implement Refund model
- [ ] Implement PaymentWebhook model
- [ ] Create admin.py for payments
- [ ] Run makemigrations for payments app
- [ ] Run migrate for payments app

#### E. Create Superuser
- [ ] python manage.py createsuperuser
- [ ] Test admin interface

---

### ✅ PHASE 3: GraphQL API (Week 3-5)

#### A. Create GraphQL Types
```
For each app, create schema.py with:
- [ ] users/schema.py - UserType, WholesaleProfileType
- [ ] products/schema.py - ProductType, CategoryType, BrandType, PriceType
- [ ] orders/schema.py - OrderType, CartType, OrderItemType
- [ ] payments/schema.py - PaymentType, RefundType
```

#### B. Implement Queries
```graphql
- [ ] Query: products (with filters)
- [ ] Query: product(id or slug)
- [ ] Query: categories
- [ ] Query: brands
- [ ] Query: cart(sessionKey)
- [ ] Query: orders (for wholesale)
- [ ] Query: order(orderNumber)
- [ ] Query: me (current user)
```

#### C. Implement Mutations
```graphql
# Cart Operations (Retail - No Auth)
- [ ] Mutation: addToCart(sessionKey, productId, quantity)
- [ ] Mutation: updateCartItem(cartItemId, quantity)
- [ ] Mutation: removeFromCart(cartItemId)
- [ ] Mutation: clearCart(sessionKey)

# Orders
- [ ] Mutation: createRetailOrder(cartId, customerInfo, shippingAddress)
- [ ] Mutation: createWholesaleOrder(items, shippingAddress) [Auth Required]

# Payments
- [ ] Mutation: initiatePayment(orderId, gatewayType)
- [ ] Mutation: confirmPayment(paymentId, gatewayResponse)

# Wholesale User (Auth Required)
- [ ] Mutation: updateMyProfile(phone, address) [For wholesale to update their own info]

# Admin Only (Staff Required)
- [ ] Mutation: createWholesaleUser(username, password, companyName, phone, creditLimit)
- [ ] Mutation: updateWholesaleUser(userId, data)
- [ ] Mutation: suspendWholesaleUser(userId)
- [ ] Mutation: updateProductPrice(productId, priceType, price)
- [ ] Mutation: updateInventory(productId, quantity)
- [ ] Mutation: updateOrderStatus(orderId, status)

# Note: No self-registration for wholesale - accounts created by admin after offline paperwork
```

#### D. Authentication & Permissions
- [ ] Set up JWT authentication
- [ ] Create custom permissions
- [ ] Implement session-based cart for retail
- [ ] Add rate limiting

---

### ✅ PHASE 4: Payment Gateway Integration (Week 5-6)

#### A. Tabby Integration
- [ ] Register for Tabby account
- [ ] Get API credentials
- [ ] Create payments/services/tabby.py
- [ ] Implement payment initiation
- [ ] Implement webhook handler
- [ ] Test with sandbox

#### B. Tamara Integration
- [ ] Register for Tamara account
- [ ] Get API credentials
- [ ] Create payments/services/tamara.py
- [ ] Implement payment initiation
- [ ] Implement webhook handler
- [ ] Test with sandbox

#### C. Network International
- [ ] Register for Network account
- [ ] Get merchant credentials
- [ ] Create payments/services/network.py
- [ ] Implement card payment flow
- [ ] Implement 3D Secure
- [ ] Implement webhook handler
- [ ] Test with sandbox

#### D. Unified Webhook System
- [ ] Create payments/webhooks.py
- [ ] Implement signature verification
- [ ] Update order status on payment
- [ ] Send confirmation emails
- [ ] Log all webhook events

---

### ✅ PHASE 5: Business Logic (Week 6-7)

#### A. Pricing Logic
- [ ] Create orders/services.py
- [ ] Implement retail price calculation
- [ ] Implement wholesale tiered pricing
- [ ] Implement VAT calculation (5%)
- [ ] Implement delivery fee by emirate
- [ ] Price snapshot on order creation

#### B. Inventory Management
- [ ] Stock reservation on order
- [ ] Stock release on cancellation
- [ ] Low stock alerts
- [ ] Out-of-stock validation
- [ ] Inventory history tracking

#### C. Order Processing
- [ ] Order validation logic
- [ ] Minimum order quantity check
- [ ] Order confirmation emails
- [ ] Status workflow automation
- [ ] Cancellation logic with refund

#### D. Cart Management
- [ ] Cart expiration logic (48 hours)
- [ ] Cart cleanup cron job
- [ ] Price validation before checkout
- [ ] Inventory check before checkout

---

### ✅ PHASE 6: Admin Dashboard (Week 7-8)

#### A. Enhance Django Admin
- [ ] Install django-admin-interface or similar
- [ ] Create custom dashboard view
- [ ] Add sales overview
- [ ] Add order statistics
- [ ] Add inventory alerts

#### B. Wholesale Management Interface
- [ ] Create wholesale user form (username, password, company, phone, credit limit)
- [ ] Edit wholesale customer details
- [ ] View customer order history
- [ ] Set custom pricing/discount per customer
- [ ] Credit limit management
- [ ] Suspend/activate wholesale accounts
- [ ] Add notes about customer (for internal use)

Note: No approval workflow needed - admin creates account after completing offline paperwork

#### C. Product Management
- [ ] Bulk product import (CSV)
- [ ] Image upload improvements
- [ ] Bulk price update
- [ ] Bulk inventory update
- [ ] Category drag-and-drop ordering

#### D. Order Management
- [ ] Order list with advanced filters
- [ ] Order detail view enhancement
- [ ] Status change interface
- [ ] Refund processing interface
- [ ] Invoice/packing slip generation

---

### ✅ PHASE 7: Additional Features (Week 8-9)

#### A. Email System
- [ ] Configure email backend (SendGrid/AWS SES)
- [ ] Create email templates
- [ ] Order confirmation email (retail)
- [ ] Order confirmation email (wholesale)
- [ ] Shipment notification
- [ ] Delivery confirmation
- [ ] New wholesale account created email (with login credentials)
- [ ] Payment failure notification
- [ ] Low stock alerts (internal to admin)

#### B. Search & Filtering
- [ ] Implement product search
- [ ] Add category filters
- [ ] Add brand filters
- [ ] Add price range filters
- [ ] Add sorting options
- [ ] Optimize search queries

#### C. Promotions (Future Phase)
- [ ] Coupon model
- [ ] Discount codes
- [ ] Flash sales
- [ ] Bundle deals
- [ ] Free shipping rules

---

### ✅ PHASE 8: Testing & Optimization (Week 9-10)

#### A. Unit Tests
- [ ] Test User models
- [ ] Test Product models
- [ ] Test Order models
- [ ] Test Payment models
- [ ] Test GraphQL queries
- [ ] Test GraphQL mutations

#### B. Integration Tests
- [ ] Test retail checkout flow
- [ ] Test wholesale ordering
- [ ] Test payment processing
- [ ] Test webhook handling

#### C. Performance Optimization
- [ ] Add database indexes
- [ ] Optimize queries with select_related
- [ ] Optimize queries with prefetch_related
- [ ] Add Redis caching
- [ ] Image optimization
- [ ] Query profiling with Django Debug Toolbar

#### D. Security Audit
- [ ] HTTPS enforcement
- [ ] CSRF protection check
- [ ] XSS prevention check
- [ ] Rate limiting implementation
- [ ] Secure payment data handling
- [ ] Environment variables audit

---

### ✅ PHASE 9: Deployment Prep (Week 10-11)

#### A. Production Database
- [ ] Install PostgreSQL
- [ ] Configure database settings
- [ ] Create database backup strategy
- [ ] Test database migrations

#### B. Static & Media Files
- [ ] Configure AWS S3 or local storage
- [ ] Set up django-storages
- [ ] Configure STATIC_ROOT
- [ ] Test file uploads
- [ ] Set up CDN (optional)

#### C. Server Setup
- [ ] Choose hosting provider
- [ ] Set up Nginx
- [ ] Set up Gunicorn
- [ ] Configure SSL certificate
- [ ] Set up domain DNS
- [ ] Configure environment variables

#### D. Monitoring
- [ ] Set up Sentry for error tracking
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Database monitoring

---

### ✅ PHASE 10: Launch (Week 11-12)

#### A. Pre-Launch Checklist
- [ ] Complete UAT testing
- [ ] Load testing
- [ ] Security audit
- [ ] Backup strategy confirmed
- [ ] Rollback plan prepared

#### B. Launch Day
- [ ] Deploy to production
- [ ] Monitor error logs
- [ ] Test critical user flows
- [ ] Monitor payment processing
- [ ] Verify email delivery

#### C. Post-Launch
- [ ] Gather user feedback
- [ ] Fix critical bugs
- [ ] Performance tuning
- [ ] Analytics tracking

---

## 🚀 QUICK START COMMANDS

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env  # Edit with your values

# 4. Make migrations
python manage.py makemigrations

# 5. Apply migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver

# 8. Access admin
# http://localhost:8000/admin

# 9. Access GraphQL
# http://localhost:8000/graphql
```

---

## 📁 RECOMMENDED PROJECT STRUCTURE

```
ecomarce_choco/
├── .env
├── .gitignore
├── requirements.txt
├── PROJECT_PLAN.md (this file)
├── README.md
├── manage.py
│
├── ecomarce_choco/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── schema.py          # Main GraphQL schema
│   ├── wsgi.py
│   └── asgi.py
│
├── users/
│   ├── models.py
│   ├── admin.py
│   ├── schema.py          # GraphQL types & queries
│   ├── mutations.py       # GraphQL mutations
│   ├── signals.py         # Django signals
│   └── tests.py
│
├── products/
│   ├── models.py
│   ├── admin.py
│   ├── schema.py
│   ├── mutations.py
│   ├── filters.py
│   ├── utils.py
│   └── tests.py
│
├── orders/
│   ├── models.py
│   ├── admin.py
│   ├── schema.py
│   ├── mutations.py
│   ├── services.py        # Business logic
│   ├── utils.py
│   └── tests.py
│
├── payments/
│   ├── models.py
│   ├── admin.py
│   ├── schema.py
│   ├── mutations.py
│   ├── webhooks.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tabby.py
│   │   ├── tamara.py
│   │   └── network.py
│   ├── utils.py
│   └── tests.py
│
├── core/                  # Shared utilities (create this)
│   ├── __init__.py
│   ├── permissions.py
│   ├── middleware.py
│   ├── decorators.py
│   └── utils.py
│
└── media/                 # Uploaded files
    ├── products/
    ├── brands/
    ├── categories/
    └── wholesale_documents/
```

---

## 🇦🇪 UAE-SPECIFIC CONSIDERATIONS

### Business Requirements
- **VAT**: 5% on all products (mandatory)
- **Currency**: AED (UAE Dirham)
- **Emirates**: Dubai, Abu Dhabi, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, Fujairah
- **Working Days**: Sunday-Thursday
- **Trade License**: Required for wholesale customers
- **Payment Preferences**: COD popular, card payments, BNPL growing

### Delivery Considerations
- Same-day delivery competitive in Dubai/Abu Dhabi
- Different delivery fees per emirate
- Delivery during prayer times consideration
- Weekend delivery (Friday-Saturday)

### Language
- Primary: English
- Secondary: Arabic (future implementation)
- RTL support for Arabic (future)

---

## 📊 EXPECTED DELIVERABLES

### Phase 1-2 (Weeks 1-3)
✅ Complete database models  
✅ Admin interface functional  
✅ Basic CRUD operations  

### Phase 3-4 (Weeks 3-6)
✅ GraphQL API fully functional  
✅ Payment gateways integrated  
✅ Retail checkout working  

### Phase 5-6 (Weeks 6-8)
✅ Business logic implemented  
✅ Wholesale ordering functional  
✅ Admin dashboard enhanced  

### Phase 7-8 (Weeks 8-10)
✅ Email notifications working  
✅ Search & filters implemented  
✅ Tests completed  
✅ Performance optimized  

### Phase 9-10 (Weeks 10-12)
✅ Production deployment  
✅ Monitoring active  
✅ System stable and live  

---

## 🎯 NEXT IMMEDIATE STEPS

1. **Install GraphQL dependencies**
   ```bash
   pip install graphene-django django-graphql-jwt django-cors-headers pillow
   pip freeze > requirements.txt
   ```

2. **Update settings.py** with new apps and configurations

3. **Implement all models** starting with users, then products, orders, payments

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser and test admin**
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

---

## 📞 SUPPORT & RESOURCES

### Django Documentation
- https://docs.djangoproject.com/

### Graphene-Django
- https://docs.graphene-python.org/projects/django/

### Payment Gateways
- Tabby: https://docs.tabby.ai/
- Tamara: https://docs.tamara.co/
- Network International: https://www.network.ae/en/developers

### UAE Business Resources
- Federal Tax Authority (VAT): https://tax.gov.ae/
- Dubai Chamber: https://www.dubaichamber.com/

---

**Last Updated**: October 12, 2025  
**Version**: 1.0  
**Project**: E-Commerce Chocolate Platform Backend

