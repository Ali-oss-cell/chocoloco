from django.db import models
from django.conf import settings
import uuid


class Cart(models.Model):
    """Shopping cart for retail customers (session-based, no login required)
    
    PHASE 1: Session-based carts for retail customers
    PHASE 2: Can also link to User for wholesale customers
    """
    session_key = models.CharField(max_length=255, unique=True, help_text="Session key for retail customers")
    # FUTURE: Uncomment when adding wholesale
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart {self.session_key}"


class CartItem(models.Model):
    """Items in cart
    
    Supports both regular products and product variants:
    - For regular products: product is set, variant is null
    - For variant products: both product and variant are set
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, null=True, blank=True, 
                                help_text="If product has variants, specify which variant")
    quantity = models.IntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        # Allow same product with different variants
        unique_together = ['cart', 'product', 'variant']
        indexes = [
            models.Index(fields=['cart'], name='cartitem_cart_idx'),
        ]

    def __str__(self):
        if self.variant:
            return f"{self.product.name} ({self.variant.sku}) x {self.quantity}"
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price_at_addition * self.quantity
    
    @property
    def display_name(self):
        """Get display name with variant info if applicable"""
        if self.variant:
            variant_options = ', '.join([vv.option_value.value for vv in self.variant.option_values.all()])
            return f"{self.product.name} - {variant_options}"
        return self.product.name


class Order(models.Model):
    """Main Order Model
    
    PHASE 1: Retail orders (guest checkout)
    PHASE 2: Add wholesale orders with user accounts
    """
    ORDER_TYPE_CHOICES = [
        ('RETAIL', 'Retail Order'),
        # FUTURE: Uncomment when adding wholesale
        # ('WHOLESALE', 'Wholesale Order'),
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
    # FUTURE: Uncomment when adding wholesale users
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='RETAIL')
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
        indexes = [
            models.Index(fields=['status'], name='order_status_idx'),
            models.Index(fields=['-created_at'], name='order_created_at_idx'),
            models.Index(fields=['status', '-created_at'], name='order_status_created_idx'),
            models.Index(fields=['order_type', 'status'], name='order_type_status_idx'),
            models.Index(fields=['order_number'], name='order_number_idx'),
        ]

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
    """Items in an order
    
    Stores snapshot of product/variant at time of order:
    - For regular products: variant fields are null
    - For variant products: variant fields are populated
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True,
                                help_text="Variant if applicable (preserved for reference)")
    
    # Snapshot fields (captured at time of order)
    product_name = models.CharField(max_length=255, help_text="Snapshot of product name")
    product_sku = models.CharField(max_length=100, help_text="Snapshot of SKU (variant SKU if applicable)")
    variant_options = models.JSONField(null=True, blank=True, 
                                      help_text="Snapshot of variant options (e.g., {'Color': 'Red', 'Weight': '500g'})")
    
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit at time of order")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        if self.variant_options:
            options_str = ', '.join([f"{k}: {v}" for k, v in self.variant_options.items()])
            return f"{self.product_name} ({options_str}) x {self.quantity}"
        return f"{self.product_name} x {self.quantity}"


class ShippingAddress(models.Model):
    """Delivery address for orders"""
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
    # FUTURE: Link to user for saved addresses
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
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
    # FUTURE: Link to user when staff accounts are used
    # changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_history'
        ordering = ['-created_at']
        verbose_name_plural = 'Order Status Histories'

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
