"""
Tamara Payment Gateway Integration
Buy Now, Pay Later (BNPL) service
"""
import requests
import json
from decimal import Decimal
from typing import Dict, Any
from django.conf import settings
from django.utils import timezone
from .base import BasePaymentService


class TamaraService(BasePaymentService):
    """
    Tamara payment gateway integration
    Handles BNPL payments with flexible installments
    """
    
    def __init__(self):
        super().__init__()
        self.gateway_name = "TAMARA"
        self.base_url = getattr(settings, 'TAMARA_BASE_URL', 'https://api-sandbox.tamara.co')
        self.api_key = getattr(settings, 'TAMARA_API_KEY', '')
        self.merchant_id = getattr(settings, 'TAMARA_MERCHANT_ID', '')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_payment_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Tamara payment session
        """
        try:
            if not self.validate_order_data(order_data):
                return self.create_error_response("Invalid order data")
            
            # Prepare Tamara payment request
            payment_request = {
                "order_reference_id": order_data['order_id'],
                "total_amount": {
                    "amount": self.format_amount(order_data['amount']),
                    "currency": order_data['currency']
                },
                "description": f"Order #{order_data['order_id']}",
                "country_code": "AE",
                "payment_type": "PAY_BY_INSTALMENTS",
                "instalments": 4,
                "items": order_data.get('items', []),
                "consumer": {
                    "first_name": order_data.get('customer_name', 'Customer').split()[0],
                    "last_name": ' '.join(order_data.get('customer_name', 'Customer').split()[1:]) if len(order_data.get('customer_name', 'Customer').split()) > 1 else '',
                    "phone_number": order_data['customer_phone'],
                    "email": order_data['customer_email']
                },
                "billing_address": {
                    "first_name": order_data.get('customer_name', 'Customer').split()[0],
                    "last_name": ' '.join(order_data.get('customer_name', 'Customer').split()[1:]) if len(order_data.get('customer_name', 'Customer').split()) > 1 else '',
                    "line1": order_data.get('billing_address', {}).get('line1', ''),
                    "city": order_data.get('billing_address', {}).get('city', ''),
                    "country_code": "AE"
                },
                "shipping_address": {
                    "first_name": order_data.get('shipping_address', {}).get('first_name', order_data.get('customer_name', 'Customer').split()[0]),
                    "last_name": order_data.get('shipping_address', {}).get('last_name', ' '.join(order_data.get('customer_name', 'Customer').split()[1:]) if len(order_data.get('customer_name', 'Customer').split()) > 1 else ''),
                    "line1": order_data.get('shipping_address', {}).get('line1', ''),
                    "city": order_data.get('shipping_address', {}).get('city', ''),
                    "country_code": "AE"
                },
                "merchant_url": {
                    "success_url": f"{settings.FRONTEND_URL}/payment/success",
                    "failure_url": f"{settings.FRONTEND_URL}/payment/failure",
                    "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel",
                    "notification_url": f"{settings.BACKEND_URL}/webhooks/tamara/"
                },
                "discount": {
                    "name": "Discount",
                    "amount": {
                        "amount": self.format_amount(order_data.get('discount_amount', 0)),
                        "currency": order_data['currency']
                    }
                },
                "tax_amount": {
                    "amount": self.format_amount(order_data.get('tax_amount', 0)),
                    "currency": order_data['currency']
                },
                "shipping_amount": {
                    "amount": self.format_amount(order_data.get('shipping_amount', 0)),
                    "currency": order_data['currency']
                }
            }
            
            # Make API request to Tamara
            response = requests.post(
                f"{self.base_url}/checkout",
                headers=self.headers,
                json=payment_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_payment_event("PAYMENT_CREATED", {
                    'order_id': order_data['order_id'],
                    'payment_id': data.get('order_id'),
                    'amount': order_data['amount']
                })
                
                return self.create_success_response(
                    payment_id=data.get('order_id'),
                    payment_url=data.get('checkout_url'),
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
                
                return self.create_error_response(f"Tamara payment creation failed: {error_message}")
                
        except requests.RequestException as e:
            self.log_payment_event("API_ERROR", {
                'order_id': order_data['order_id'],
                'error': str(e)
            })
            return self.create_error_response(f"Tamara API error: {str(e)}")
        
        except Exception as e:
            self.log_payment_event("UNEXPECTED_ERROR", {
                'order_id': order_data['order_id'],
                'error': str(e)
            })
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Verify payment status with Tamara
        """
        try:
            response = requests.get(
                f"{self.base_url}/orders/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                status_mapping = {
                    'PENDING': 'pending',
                    'APPROVED': 'authorized',
                    'COMPLETED': 'completed',
                    'EXPIRED': 'expired',
                    'DECLINED': 'failed',
                    'CANCELLED': 'cancelled'
                }
                
                status = status_mapping.get(data.get('status'), 'unknown')
                amount = self.parse_amount(data.get('total_amount', {}).get('amount', '0'))
                
                self.log_payment_event("PAYMENT_VERIFIED", {
                    'payment_id': payment_id,
                    'status': status,
                    'amount': amount
                })
                
                return self.create_success_response(
                    status=status,
                    amount=amount,
                    transaction_id=data.get('order_id'),
                    gateway_response=data
                )
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('message', f'HTTP {response.status_code}')
                
                return self.create_error_response(f"Tamara verification failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Tamara API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Tamara webhook notifications
        """
        try:
            # Verify webhook signature (implement based on Tamara docs)
            # signature = payload.get('signature')
            # if not self.verify_webhook_signature(payload, signature):
            #     return self.create_error_response("Invalid webhook signature")
            
            payment_id = payload.get('order_id')
            status = payload.get('status')
            amount = self.parse_amount(payload.get('total_amount', {}).get('amount', '0'))
            
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
        Process refund through Tamara
        """
        try:
            refund_request = {
                "refund_id": f"REF_{payment_id}_{timezone.now().timestamp()}",
                "total_amount": {
                    "amount": self.format_amount(amount),
                    "currency": "AED"
                },
                "refund_type": "FULL" if amount == 0 else "PARTIAL",
                "reason": reason or "Customer requested refund"
            }
            
            response = requests.post(
                f"{self.base_url}/refunds",
                headers=self.headers,
                json=refund_request,
                timeout=30
            )
            
            if response.status_code == 200:
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
                
                return self.create_error_response(f"Tamara refund failed: {error_message}")
                
        except requests.RequestException as e:
            return self.create_error_response(f"Tamara API error: {str(e)}")
        
        except Exception as e:
            return self.create_error_response(f"Unexpected error: {str(e)}")
    
    def get_payment_methods(self) -> Dict[str, Any]:
        """
        Get available Tamara payment methods
        """
        try:
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
