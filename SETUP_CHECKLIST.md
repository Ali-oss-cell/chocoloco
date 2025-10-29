# 🚀 Quick Setup Checklist

Use this checklist to get your project up and running quickly.

## ✅ Initial Setup (15-30 minutes)

### 1. Environment Setup
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Install core dependencies: `pip install graphene-django django-graphql-jwt django-cors-headers pillow python-decouple django-filter`
- [ ] Update requirements: `pip freeze > requirements.txt`

### 2. Environment Variables
- [ ] Copy `env_template.txt` to create `.env` file
- [ ] Update `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=True` for development
- [ ] Configure `ALLOWED_HOSTS`

### 3. Settings Configuration
Update `ecomarce_choco/settings.py`:

```python
# Add to INSTALLED_APPS
'graphene_django',
'corsheaders',
'django_filters',

# Add to MIDDLEWARE (after SecurityMiddleware)
'corsheaders.middleware.CorsMiddleware',

# Add at the end of settings.py
import os
from decouple import config

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# GraphQL
GRAPHENE = {
    'SCHEMA': 'ecomarce_choco.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

# Authentication
AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Time zone
TIME_ZONE = 'Asia/Dubai'
```

## ✅ Database Models Implementation (2-4 hours)

### 4. Users App
- [ ] Open `users/models.py`
- [ ] Copy User model from PROJECT_PLAN.md
- [ ] Copy WholesaleProfile model from PROJECT_PLAN.md
- [ ] Save file

### 5. Products App
- [ ] Open `products/models.py`
- [ ] Copy all 7 models from PROJECT_PLAN.md:
  - [ ] Category
  - [ ] Brand
  - [ ] Product
  - [ ] ProductImage
  - [ ] ProductPrice
  - [ ] Inventory
  - [ ] ProductReview
- [ ] Save file

### 6. Orders App
- [ ] Open `orders/models.py`
- [ ] Copy all 6 models from PROJECT_PLAN.md:
  - [ ] Cart
  - [ ] CartItem
  - [ ] Order
  - [ ] OrderItem
  - [ ] ShippingAddress
  - [ ] OrderStatusHistory
- [ ] Save file

### 7. Payments App
- [ ] Open `payments/models.py`
- [ ] Copy all 4 models from PROJECT_PLAN.md:
  - [ ] PaymentGateway
  - [ ] Payment
  - [ ] Refund
  - [ ] PaymentWebhook
- [ ] Save file

## ✅ Migrations & Admin (30 minutes)

### 8. Create & Apply Migrations
```bash
# Create migrations
python manage.py makemigrations users
python manage.py makemigrations products
python manage.py makemigrations orders
python manage.py makemigrations payments

# Apply all migrations
python manage.py migrate
```

### 9. Create Superuser
```bash
python manage.py createsuperuser
# Enter username, email, and password
```

### 10. Test Admin Interface
```bash
python manage.py runserver
# Visit: http://localhost:8000/admin
# Login with superuser credentials
```

## ✅ Admin Configuration (1-2 hours)

### 11. Users Admin
Create/update `users/admin.py`:
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WholesaleProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Simplified user admin - create wholesale accounts after offline paperwork"""
    list_display = ['username', 'email', 'user_type', 'company_name', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'company_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Business Information', {
            'fields': ('user_type', 'phone_number', 'company_name', 'credit_limit')
        }),
    )
    
    # Make it easy to create wholesale users
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Business Information', {
            'fields': ('user_type', 'company_name', 'phone_number', 'credit_limit')
        }),
    )

@admin.register(WholesaleProfile)
class WholesaleProfileAdmin(admin.ModelAdmin):
    """Simple profile for storing additional wholesale customer details"""
    list_display = ['user', 'payment_terms', 'discount_percentage', 'created_at']
    list_filter = ['payment_terms']
    search_fields = ['user__username', 'user__company_name', 'company_address']
    
    # Note: Profile is auto-created via signal when wholesale user is created
```

### 12. Products Admin
Create/update `products/admin.py`:
```python
from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductPrice, Inventory, ProductReview

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 2

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'is_active', 'display_order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_of_origin', 'is_active', 'display_order']
    list_filter = ['is_active', 'country_of_origin']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'brand', 'category', 'is_active', 'featured']
    list_filter = ['is_active', 'featured', 'brand', 'category']
    search_fields = ['name', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductPriceInline]

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_in_stock', 'reserved_quantity', 'available_quantity', 'is_low_stock']
    list_filter = ['last_restocked_at']
    search_fields = ['product__name']
```

### 13. Orders Admin
Create/update `orders/admin.py`:
```python
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'unit_price', 'total_price']

class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'order_type', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'order_type', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, ShippingAddressInline]
    
    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered']
    
    def mark_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
    mark_confirmed.short_description = "Mark selected orders as Confirmed"
```

### 14. Payments Admin
Create/update `payments/admin.py`:
```python
from django.contrib import admin
from .models import PaymentGateway, Payment, Refund, PaymentWebhook

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_active', 'is_test_mode']
    list_filter = ['is_active', 'is_test_mode']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'gateway', 'amount', 'status', 'created_at']
    list_filter = ['status', 'gateway', 'payment_method']
    search_fields = ['payment_id', 'order__order_number']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['refund_id', 'order__order_number']
```

## ✅ Test Data Creation (30 minutes)

### 15. Create Test Data via Admin
- [ ] Create 2-3 Categories (Dark Chocolate, Milk Chocolate, White Chocolate)
- [ ] Create 2-3 Brands (e.g., Lindt, Ferrero, Patchi)
- [ ] Create 5-10 Products with:
  - [ ] Basic information
  - [ ] Product images
  - [ ] Retail prices
  - [ ] Wholesale prices
  - [ ] Inventory stock
- [ ] Create 1-2 test wholesale users
- [ ] Create 1-2 test orders

## ✅ Next Phase: GraphQL Setup

After completing the above, proceed to **Phase 3** in PROJECT_PLAN.md for GraphQL implementation.

### Quick Reference
- **Detailed Guide**: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Project Overview**: [README.md](README.md)
- **Environment Template**: env_template.txt
- **Full Requirements**: requirements_full.txt

---

## 🎯 Estimated Time to Complete
- **Initial Setup**: 15-30 minutes
- **Database Models**: 2-4 hours
- **Migrations & Admin**: 30 minutes
- **Admin Configuration**: 1-2 hours
- **Test Data**: 30 minutes

**Total: 5-8 hours** to get a fully functional admin interface with all models working.

---

## 📞 Need Help?
Refer to PROJECT_PLAN.md for:
- Detailed model code
- GraphQL implementation
- Payment gateway integration
- Business logic examples
- Deployment guides

