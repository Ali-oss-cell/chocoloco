from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended User Model for Staff (and future Wholesale Customers)
    
    LAUNCH STRATEGY:
    - Phase 1 (NOW): Just staff/admin users for managing the store
    - Phase 2 (FUTURE): Add wholesale customer accounts after offline paperwork
    
    For now, only staff users are needed. Retail customers don't need accounts!
    """
    # Keep minimal fields for now - ready for wholesale expansion later
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.username


# ==============================================================================
# FUTURE FEATURE: Wholesale Customer Support
# ==============================================================================
# Uncomment these models when you're ready to add wholesale customers
# For now, focus on retail (no login required)
# ==============================================================================

# class WholesaleProfile(models.Model):
#     """Additional details for wholesale customers (created by admin after offline paperwork)
#     
#     TO ENABLE WHOLESALE:
#     1. Uncomment this model
#     2. Add wholesale fields to User model above (user_type, company_name, credit_limit)
#     3. Run: python manage.py makemigrations
#     4. Run: python manage.py migrate
#     5. Update admin.py to include wholesale management
#     """
#     PAYMENT_TERMS_CHOICES = [
#         ('COD', 'Cash on Delivery'),
#         ('NET30', 'Net 30 Days'),
#         ('NET60', 'Net 60 Days'),
#         ('PREPAID', 'Prepaid'),
#     ]
#     
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wholesale_profile')
#     company_name = models.CharField(max_length=255)
#     company_address = models.TextField(blank=True)
#     payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='COD')
#     discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Special discount for this customer")
#     credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Credit limit in AED")
#     minimum_order_quantity = models.IntegerField(default=1, help_text="Minimum order quantity in units")
#     notes = models.TextField(blank=True, help_text="Internal notes about this customer")
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'wholesale_profiles'
#         
#     def __str__(self):
#         return f"Wholesale Profile - {self.company_name}"
