"""
Payment webhook views
Handle webhooks from payment gateways
"""
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .services.manager import payment_manager

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TabbyWebhookView(View):
    """Handle Tabby webhook notifications"""
    
    def post(self, request):
        try:
            # Parse JSON payload
            payload = json.loads(request.body)
            
            # Log webhook
            logger.info(f"Tabby webhook received: {payload}")
            
            # Process webhook through payment manager
            result = payment_manager.handle_webhook(payload, 'TABBY')
            
            if result['success']:
                logger.info(f"Tabby webhook processed successfully: {result}")
                return JsonResponse({'status': 'success', 'message': 'Webhook processed'})
            else:
                logger.error(f"Tabby webhook processing failed: {result}")
                return JsonResponse({'status': 'error', 'message': result.get('error', 'Processing failed')}, status=400)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Tabby webhook")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Tabby webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TamaraWebhookView(View):
    """Handle Tamara webhook notifications"""
    
    def post(self, request):
        try:
            # Parse JSON payload
            payload = json.loads(request.body)
            
            # Log webhook
            logger.info(f"Tamara webhook received: {payload}")
            
            # Process webhook through payment manager
            result = payment_manager.handle_webhook(payload, 'TAMARA')
            
            if result['success']:
                logger.info(f"Tamara webhook processed successfully: {result}")
                return JsonResponse({'status': 'success', 'message': 'Webhook processed'})
            else:
                logger.error(f"Tamara webhook processing failed: {result}")
                return JsonResponse({'status': 'error', 'message': result.get('error', 'Processing failed')}, status=400)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Tamara webhook")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Tamara webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ZiinaWebhookView(View):
    """Handle Ziina webhook notifications"""
    
    def post(self, request):
        try:
            # Parse JSON payload
            payload = json.loads(request.body)
            
            # Log webhook
            logger.info(f"Ziina webhook received: {payload}")
            
            # Process webhook through payment manager
            result = payment_manager.handle_webhook(payload, 'ZIINA')
            
            if result['success']:
                # Update payment status
                payment_id = result.get('payment_id')
                status = result.get('status', '').upper()
                
                try:
                    from .models import Payment
                    from orders.models import Order, OrderStatusHistory
                    from django.utils import timezone
                    
                    # Find payment by payment_id
                    payment = Payment.objects.get(payment_id=payment_id)
                    
                    # Update payment status
                    payment.status = status
                    payment.gateway_response = payload
                    if status in ['COMPLETED', 'SUCCESS', 'CAPTURED']:
                        payment.captured_at = timezone.now()
                    payment.save()
                    
                    # Update order status if payment successful
                    if status in ['COMPLETED', 'SUCCESS', 'CAPTURED']:
                        order = payment.order
                        if order.status == 'PENDING':
                            order.status = 'CONFIRMED'
                            order.confirmed_at = timezone.now()
                            order.save()
                            
                            # Create status history
                            OrderStatusHistory.objects.create(
                                order=order,
                                status='CONFIRMED',
                                notes=f'Payment confirmed via Ziina - Payment ID: {payment_id}'
                            )
                            
                            # Deduct inventory (reserved → deducted)
                            from products.models import Product, ProductVariant
                            for item in order.items.all():
                                if item.variant:
                                    # Deduct from variant
                                    variant = item.variant
                                    variant.reserved_quantity = max(0, variant.reserved_quantity - item.quantity)
                                    variant.quantity_in_stock = max(0, variant.quantity_in_stock - item.quantity)
                                    variant.save()
                                else:
                                    # Deduct from product inventory
                                    if hasattr(item.product, 'inventory'):
                                        inventory = item.product.inventory
                                        inventory.reserved_quantity = max(0, inventory.reserved_quantity - item.quantity)
                                        inventory.quantity_in_stock = max(0, inventory.quantity_in_stock - item.quantity)
                                        inventory.save()
                            
                            logger.info(f"Order {order.order_number} confirmed and inventory deducted for customer {order.customer_name}")
                    
                except Payment.DoesNotExist:
                    logger.warning(f"Payment {payment_id} not found in database")
                except Exception as e:
                    logger.error(f"Error updating order from webhook: {str(e)}", exc_info=True)
                
                logger.info(f"Ziina webhook processed successfully: {result}")
                return JsonResponse({'status': 'success', 'message': 'Webhook processed'})
            else:
                logger.error(f"Ziina webhook processing failed: {result}")
                return JsonResponse({'status': 'error', 'message': result.get('error', 'Processing failed')}, status=400)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Ziina webhook")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Ziina webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


# Legacy function-based views for compatibility
@csrf_exempt
@require_http_methods(["POST"])
def tabby_webhook(request):
    """Tabby webhook endpoint (function-based)"""
    view = TabbyWebhookView()
    return view.post(request)


@csrf_exempt
@require_http_methods(["POST"])
def tamara_webhook(request):
    """Tamara webhook endpoint (function-based)"""
    view = TamaraWebhookView()
    return view.post(request)

