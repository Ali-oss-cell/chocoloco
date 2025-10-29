"""
Tabby Payment Gateway Integration
Buy Now, Pay Later (BNPL) service
"""
import requests
import json
from decimal import Decimal
from typing import Dict, Any
from django.conf import settings
from django.utils import timezone
from .base import BasePaymentService


class TabbyService(BasePaymentService):
    """
    Tabby payment gateway integration
    Handles BNPL payments with 4 installments
    """
    
    def __init__(self):
        super().__init__()
        self.gateway_name = "TABBY"
        self.base_url = getattr(settings, 'TABBY_BASE_URL', 'https://api-sandbox.tabby.ai')
        self.api_key = getattr(settings, 'TABBY_API_KEY', '')
        self.merchant_code = getattr(settings, 'TABBY_MERCHANT_CODE', '')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_payment_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Tabby payment session
        """
        try:
            if not self.validate_order_data(order_data):
                return self.create_error_response("Invalid order data")
            
            # Prepare Tabby payment request
            payment_request = {
                "payment": {
                    "amount": self.format_amount(order_data['amount']),
                    "currency": order_data['currency'],
                    "description": f"Order #{order_data['order_id']}",
                    "buyer": {
                        "phone": order_data['customer_phone'],
                        "email": order_data['customer_email'],
                        "name": order_data.get('customer_name', 'Customer')
                    },
                    "buyer_history": {
                        "registered_since": "2020-01-01T00:00:00Z",
                        "loyalty_level": 0
                    },
                    "order": {
                        "tax_amount": self.format_amount(order_data.get('tax_amount', 0)),
                        "shipping_amount": self.format_amount(order_data.get('shipping_amount', 0)),
                        "discount_amount": self.format_amount(order_data.get('discount_amount', 0)),
                        "updated_at": timezone.now().isoformat(),
                        "reference_id": order_data['order_id'],
                        "items": order_data.get('items', [])
                    },
                    "order_history": [
                        {
                            "purchased_at": timezone.now().isoformat(),
                            "amount": self.format_amount(order_data['amount']),
                            "payment_method": "card",
                            "status": "new"
                        }
                    ],
                    "meta": {
                        "order_id": order_data['order_id'],
                        "customer": order_data.get('customer_id'),
                        "source": "api"
                    }
                },
                "lang": "en",
                "merchant_code": self.merchant_code,
                "merchant_urls": {
                    "success": f"{settings.FRONTEND_URL}/payment/success",
                    "cancel": f"{settings.FRONTEND_URL}/payment/cancel",
                    "failure": f"{settings.FRONTEND_URL}/payment/failure"
                }
            }
            
            # Make API request to Tabby
            response = requests.post(
                f"{self.base_url}/api/v2/payments",
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
                    payment_url=data.get('configuration', {}).get('available_products', [{}])[0].get('web_url'),
                    expires_at=self.get_expiry_time(15),
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
                
                return self.create_error_response(f"Tabby payment creation failed: {error_message}")
                
        except requests.RequestException as e:
            self.log_payment_event("API_ERROR", {
                'order_id': order_data['order_id'],
                'error': str(e)
            })
            return self.create_error_response(f"Tabby API error: {str(e)}")
        
        except Exception as e:
            self.log_payment_event("UNEXPECTED_ERROR", {
                'order_id': order_data['order_id'],
                'error': str(e)
            })
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Verify payment status with Tabby
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/payments/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                payment = data.get('payment', {})
                
                status_mapping = {
                    'CREATED': 'pending',
                    'AUTHORIZED': 'authorized',
                    'CLOSED': 'completed',
                    'EXPIRED': 'expired',
                    'REJECTED': 'failed',
                    'CANCELLED': 'cancelled'
                }
                
                status = status_mapping.get(payment.get('status'), 'unknown')
                amount = self.parse_amount(payment.get('amount', '0'))
                
                self.log_payment_event("PAYMENT_VERIFIED", {
                    'payment_id': payment_id,
                    'status': status,
                    'amount': amount
                })
                
                return self.create_success_response(
                    status=status,
                    amount=amount,
                    transaction_id=payment.get('id'),
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Tabby verification failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Tabby API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Tabby webhook notifications
        """
        try:
            # Verify webhook signature (implement based on Tabby docs)
            # signature = payload.get('signature')
            # if not self.verify_webhook_signature(payload, signature):
            #     return self.create_error_response("Invalid webhook signature")
            
            payment_id = payload.get('id')
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
        Process refund through Tabby
        """
        try:
            refund_request = {
                "amount": self.format_amount(amount),
                "reason": reason or "Customer requested refund"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v2/payments/{payment_id}/refunds",
                headers=self.headers,
                json=refund_request,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                
                self.log_payment_event("REFUND_CREATED", {
                    'payment_id': payment_id,
                    'refund_amount': amount,
                    'refund_id': data.get('id')
                })
                
                return self.create_success_response(
                    refund_id=data.get('id'),
                    amount=amount,
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Tabby refund failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Tabby API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def get_payment_methods(self) -> Dict[str, Any]:
        """
        Get available Tabby payment methods
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/payment_methods",
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
