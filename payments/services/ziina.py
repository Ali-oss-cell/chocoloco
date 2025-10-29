"""
Ziina Payment Gateway Integration
UAE Central Bank licensed instant payments with Apple Pay support
"""
import requests
import json
import hashlib
import hmac
from decimal import Decimal
from typing import Dict, Any
from django.conf import settings
from django.utils import timezone
from .base import BasePaymentService


class ZiinaService(BasePaymentService):
    """
    Ziina payment gateway integration
    UAE Central Bank licensed instant payments with Apple Pay support
    """
    
    def __init__(self):
        super().__init__()
        self.gateway_name = "ZIINA"
        self.base_url = getattr(settings, 'ZIINA_BASE_URL', 'https://api-v2.ziina.com')
        self.api_key = getattr(settings, 'ZIINA_API_KEY', '')
        self.merchant_id = getattr(settings, 'ZIINA_MERCHANT_ID', '')
        self.public_key = getattr(settings, 'ZIINA_PUBLIC_KEY', '')
        self.webhook_secret = getattr(settings, 'ZIINA_WEBHOOK_SECRET', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'X-Merchant-ID': self.merchant_id
        }
    
    def create_payment_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Ziina payment session
        """
        try:
            if not self.validate_order_data(order_data):
                return self.create_error_response("Invalid order data")
            
            # Prepare Ziina payment request according to official API
            # Amount must be in base units (e.g., 1050 for AED 10.50)
            amount_in_cents = int(float(order_data['amount']) * 100)
            
            payment_request = {
                "amount": amount_in_cents,
                "currency_code": order_data['currency'],
                "message": f"Chocolate Order #{order_data['order_id']}",
                "success_url": f"{settings.FRONTEND_URL}/payment/success",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel",
                "failure_url": f"{settings.FRONTEND_URL}/payment/failure",
                "test": getattr(settings, 'ZIINA_TEST_MODE', True),  # Test mode for development
                "expiry": str(int(timezone.now().timestamp() * 1000) + (15 * 60 * 1000)),  # 15 minutes from now
                "allow_tips": False
            }
            
            # Make API request to Ziina (using official API endpoint)
            response = requests.post(
                f"{self.base_url}/api/payment_intent",
                headers=self.headers,
                json=payment_request,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                
                self.log_payment_event("PAYMENT_CREATED", {
                    'order_id': order_data['order_id'],
                    'payment_id': data.get('id'),
                    'amount': order_data['amount']
                })
                
                return self.create_success_response(
                    payment_id=data.get('id'),
                    payment_url=data.get('redirect_url'),
                    expires_at=data.get('expiry'),
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                self.log_payment_event("PAYMENT_FAILED", {
                    'order_id': order_data['order_id'],
                    'error': error_message,
                    'status_code': response.status_code
                })
                
                return self.create_error_response(f"Ziina payment creation failed: {error_message}")
                
        except requests.RequestException as e:
            self.log_payment_event("API_ERROR", {
                'order_id': order_data['order_id'],
                'error': str(e)
            })
            return self.create_error_response(f"Ziina API error: {str(e)}")
        
        except Exception as e:
            self.log_payment_event("UNEXPECTED_ERROR", {
                'order_id': order_data['order_id'],
                'error': str(e)
            })
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Verify payment status with Ziina
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/payment_intent/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                status_mapping = {
                    'requires_payment_instrument': 'pending',
                    'requires_user_action': 'pending',
                    'pending': 'pending',
                    'completed': 'completed',
                    'failed': 'failed',
                    'canceled': 'cancelled'
                }
                
                status = status_mapping.get(data.get('status'), 'unknown')
                # Amount is returned in base units, convert back to decimal
                amount_in_cents = data.get('amount', 0)
                amount = Decimal(str(amount_in_cents)) / 100
                
                self.log_payment_event("PAYMENT_VERIFIED", {
                    'payment_id': payment_id,
                    'status': status,
                    'amount': amount
                })
                
                return self.create_success_response(
                    status=status,
                    amount=amount,
                    transaction_id=data.get('transaction_id'),
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Ziina verification failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Ziina API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Ziina webhook notifications
        """
        try:
            # Verify webhook signature
            signature = payload.get('signature')
            if not self._verify_webhook_signature(payload, signature):
                return self.create_error_response("Invalid webhook signature")
            
            payment_id = payload.get('payment_id')
            status = payload.get('status')
            amount = self.parse_amount(payload.get('amount', '0'))
            
            self.log_payment_event("WEBHOOK_RECEIVED", {
                'payment_id': payment_id,
                'status': status,
                'amount': amount
            })
            
            return self.create_success_response(
                payment_id=payment_id,
                status=status,
                amount=amount,
                gateway_response=payload
            )
            
        except Exception as e:
            return self.create_error_response(f"Webhook processing error: {str(e)}")
    
    def refund_payment(self, payment_id: str, amount: Decimal, reason: str = None) -> Dict[str, Any]:
        """
        Process refund through Ziina
        """
        try:
            refund_request = {
                "payment_id": payment_id,
                "amount": self.format_amount(amount),
                "currency": "AED",
                "reason": reason or "Customer requested refund",
                "refund_id": f"REF_{payment_id}_{int(timezone.now().timestamp())}"
            }
            
            response = requests.post(
                f"{self.base_url}/refund",
                headers=self.headers,
                json=refund_request,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                
                self.log_payment_event("REFUND_CREATED", {
                    'payment_id': payment_id,
                    'refund_amount': amount,
                    'refund_id': data.get('refund_id')
                })
                
                return self.create_success_response(
                    refund_id=data.get('refund_id'),
                    amount=amount,
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Ziina refund failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Ziina API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def _verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verify webhook signature from Ziina
        """
        try:
            # Remove signature from payload for verification
            payload_copy = payload.copy()
            payload_copy.pop('signature', None)
            
            # Create signature string
            signature_string = json.dumps(payload_copy, sort_keys=True)
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False
    
    def register_webhook(self, webhook_url: str, secret: str = None) -> Dict[str, Any]:
        """
        Register webhook endpoint with Ziina
        Based on official API: POST /api/webhook
        """
        try:
            webhook_request = {
                "url": webhook_url,
                "secret": secret or self.webhook_secret
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhook",
                headers=self.headers,
                json=webhook_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_payment_event("WEBHOOK_REGISTERED", {
                    'webhook_url': webhook_url,
                    'success': data.get('success', False)
                })
                
                return self.create_success_response(
                    success=data.get('success', True),
                    error=data.get('error'),
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Webhook registration failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Ziina API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")

    def get_payment_methods(self) -> Dict[str, Any]:
        """
        Get available Ziina payment methods
        """
        try:
            # Note: Payment methods endpoint not documented in official API
            # May need to verify with Ziina support
            response = requests.get(
                f"{self.base_url}/payment-methods",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return self.create_success_response(
                    methods=response.json(),
                    gateway_response=response.json()
                )
            else:
                return self.create_error_response("Failed to get payment methods")
                
        except Exception as e:
            return self.create_error_response(f"Error getting payment methods: {str(e)}")
    
    def get_apple_pay_config(self) -> Dict[str, Any]:
        """
        Get Apple Pay configuration for frontend
        """
        try:
            return self.create_success_response(
                public_key=self.public_key,
                merchant_id=self.merchant_id,
                domain=settings.FRONTEND_URL.replace('http://', '').replace('https://', ''),
                gateway_response={
                    "apple_pay_enabled": True,
                    "supported_networks": ["visa", "mastercard", "amex"],
                    "merchant_capabilities": ["3DS"]
                }
            )
        except Exception as e:
            return self.create_error_response(f"Error getting Apple Pay config: {str(e)}")
    
    def create_apple_pay_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Apple Pay session for direct payment
        """
        try:
            apple_pay_request = {
                "merchant_id": self.merchant_id,
                "order_id": order_data['order_id'],
                "amount": self.format_amount(order_data['amount']),
                "currency": order_data['currency'],
                "customer": {
                    "email": order_data['customer_email'],
                    "phone": order_data['customer_phone'],
                    "name": order_data.get('customer_name', 'Customer')
                },
                "shipping_address": order_data.get('shipping_address', {}),
                "items": order_data.get('items', []),
                "return_url": f"{settings.FRONTEND_URL}/payment/success",
                "webhook_url": f"{settings.BACKEND_URL}/webhooks/ziina/",
                "payment_method": "apple_pay"
            }
            
            # Note: Apple Pay endpoint not documented in official API
            # May need to verify with Ziina support
            response = requests.post(
                f"{self.base_url}/apple-pay/sessions",
                headers=self.headers,
                json=apple_pay_request,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                
                return self.create_success_response(
                    session_id=data.get('session_id'),
                    payment_url=data.get('payment_url'),
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Apple Pay session creation failed: {error_message}")
                
        except Exception as e:
            return self.create_error_response(f"Apple Pay error: {str(e)}")
