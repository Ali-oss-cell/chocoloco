from django.db import models
from django.conf import settings
import uuid


class PaymentGateway(models.Model):
    """Payment gateway configuration"""
    GATEWAY_CHOICES = [
        ('TABBY', 'Tabby'),
        ('TAMARA', 'Tamara'),
        ('ZIINA', 'Ziina'),
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
        ('APPLE_PAY', 'Apple Pay'),
        ('GOOGLE_PAY', 'Google Pay'),
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
    # FUTURE: Link to staff user who processed refund
    # processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
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
