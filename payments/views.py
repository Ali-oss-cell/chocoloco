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

