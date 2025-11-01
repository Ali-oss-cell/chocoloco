from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product Categories with nested support (e.g., Dark Chocolate, Milk Chocolate)"""
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
        indexes = [
            models.Index(fields=['is_active'], name='category_is_active_idx'),
            models.Index(fields=['parent_category', 'is_active'], name='category_parent_active_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Chocolate Brands (e.g., Lindt, Ferrero, Patchi)"""
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
        indexes = [
            models.Index(fields=['is_active'], name='brand_is_active_idx'),
        ]

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
        ('LITER', 'Liter'),
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
        indexes = [
            models.Index(fields=['is_active'], name='product_is_active_idx'),
            models.Index(fields=['featured'], name='product_featured_idx'),
            models.Index(fields=['-created_at'], name='product_created_at_idx'),
            models.Index(fields=['is_active', 'featured'], name='product_active_featured_idx'),
            models.Index(fields=['category', 'is_active'], name='product_category_active_idx'),
            models.Index(fields=['brand', 'is_active'], name='product_brand_active_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductImage(models.Model):
    """Base product images (main product shots) - max 3 per product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        ordering = ['display_order']
        constraints = [
            models.CheckConstraint(
                check=models.Q(display_order__gte=1) & models.Q(display_order__lte=3),
                name='base_image_display_order_range'
            )
        ]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductImageUseCase(models.Model):
    """Simple product use case images (up to 4, optional)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='usecase_images')
    image = models.ImageField(upload_to='products/usecase/')
    display_order = models.IntegerField(default=0, help_text="Order 1-4")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_usecase_images'
        ordering = ['display_order']
        constraints = [
            models.CheckConstraint(
                check=models.Q(display_order__gte=1) & models.Q(display_order__lte=4),
                name='usecase_display_order_range'
            )
        ]

    def __str__(self):
        return f"Use case image for {self.product.name} (#{self.display_order})"


class ProductPrice(models.Model):
    """Product Pricing
    
    PHASE 1 (NOW): Just retail pricing
    PHASE 2 (FUTURE): Add wholesale pricing tier
    """
    PRICE_TYPE_CHOICES = [
        ('RETAIL', 'Retail Price'),
        # FUTURE: Uncomment when adding wholesale
        # ('WHOLESALE', 'Wholesale Price'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price_type = models.CharField(max_length=20, choices=PRICE_TYPE_CHOICES, default='RETAIL')
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
        indexes = [
            models.Index(fields=['product', 'price_type', 'is_active'], name='price_product_type_active_idx'),
            models.Index(fields=['is_active'], name='price_is_active_idx'),
        ]

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
    """Customer reviews (optional feature)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    # FUTURE: Link to User model when wholesale is added
    # user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
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


class ProductVariantOption(models.Model):
    """
    Product Variant Options (e.g., Color: [White, Dark], Weight: [500g, 1000g])
    
    This defines what options are available for a product.
    Example:
        Product: Coco Mass
        Option 1: Color (White, Dark)
        Option 2: Weight (500g, 1000g)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant_options')
    name = models.CharField(max_length=100, help_text="Option name (e.g., Color, Weight, Size)")
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_variant_options'
        ordering = ['display_order', 'name']
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductVariantOptionValue(models.Model):
    """
    Values for each variant option (e.g., White, Dark for Color option)
    
    Example:
        Option: Color
        Values: White, Dark
    """
    option = models.ForeignKey(ProductVariantOption, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100, help_text="Option value (e.g., White, Dark, 500g)")
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_variant_option_values'
        ordering = ['display_order', 'value']
        unique_together = ['option', 'value']
    
    def __str__(self):
        return f"{self.option.name}: {self.value}"


class ProductVariant(models.Model):
    """
    Actual Product Variants (combinations of options)
    
    Example:
        Variant 1: Coco Mass - White, 500g (SKU: COCO-WHITE-500)
        Variant 2: Coco Mass - White, 1000g (SKU: COCO-WHITE-1000)
        Variant 3: Coco Mass - Dark, 500g (SKU: COCO-DARK-500)
        Variant 4: Coco Mass - Dark, 1000g (SKU: COCO-DARK-1000)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, help_text="Unique SKU for this variant")
    
    # Variant-specific pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this variant")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='AED')
    
    # Variant-specific inventory
    quantity_in_stock = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    
    # Variant-specific details
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Weight for this variant")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Is this the default variant?")
    
    # Variant image (optional - can override main product image)
    image = models.ImageField(upload_to='variants/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variants'
        ordering = ['is_default', '-created_at']
    
    @property
    def available_quantity(self):
        """Calculate available quantity"""
        return self.quantity_in_stock - self.reserved_quantity
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock"""
        return self.available_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if variant is low on stock"""
        return self.available_quantity <= self.low_stock_threshold
    
    @property
    def effective_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price
    
    def __str__(self):
        option_values = ', '.join([vo.value for vo in self.option_values.all()])
        return f"{self.product.name} - {option_values} ({self.sku})"


class ProductVariantValue(models.Model):
    """
    Link between variants and their option values
    
    Example:
        Variant: COCO-WHITE-500
        Values: 
          - Color = White
          - Weight = 500g
    """
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='option_values')
    option_value = models.ForeignKey(ProductVariantOptionValue, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'product_variant_values'
        unique_together = ['variant', 'option_value']
    
    def __str__(self):
        return f"{self.variant.sku} - {self.option_value}"
