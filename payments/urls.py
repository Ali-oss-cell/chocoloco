"""
Payment URLs
Webhook endpoints for payment gateways
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Webhook endpoints
    path('webhooks/tabby/', views.TabbyWebhookView.as_view(), name='tabby_webhook'),
    path('webhooks/tamara/', views.TamaraWebhookView.as_view(), name='tamara_webhook'),
    path('webhooks/ziina/', views.ZiinaWebhookView.as_view(), name='ziina_webhook'),
    
    # Legacy webhook endpoints (function-based)
    path('webhooks/tabby/legacy/', views.tabby_webhook, name='tabby_webhook_legacy'),
    path('webhooks/tamara/legacy/', views.tamara_webhook, name='tamara_webhook_legacy'),
]
