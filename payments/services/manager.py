"""
Payment Service Manager
Manages all payment gateways and provides unified interface
"""
from typing import Dict, Any, Optional
from decimal import Decimal
from django.conf import settings
from .tabby import TabbyService
from .tamara import TamaraService
from .ziina import ZiinaService


class PaymentManager:
    """
    Central payment manager that handles all payment gateways
    Provides unified interface for payment operations
    """
    
    def __init__(self):
        self.gateways = {
            'TABBY': TabbyService(),
            'TAMARA': TamaraService(),
            'ZIINA': ZiinaService()
        }
        self.default_gateway = getattr(settings, 'DEFAULT_PAYMENT_GATEWAY', 'TABBY')
    
    def get_gateway(self, gateway_name: str):
        """Get payment gateway service by name"""
        gateway = self.gateways.get(gateway_name.upper())
        if not gateway:
            raise ValueError(f"Unknown payment gateway: {gateway_name}")
        return gateway
    
    def create_payment_session(self, order_data: Dict[str, Any], gateway_name: str = None) -> Dict[str, Any]:
        """
        Create payment session with specified gateway
        
        Args:
            order_data: Order information
            gateway_name: Payment gateway to use (TABBY, TAMARA, ZIINA)
        
        Returns:
            Dict with payment session details
        """
        if not gateway_name:
            gateway_name = self.default_gateway
        
        gateway = self.get_gateway(gateway_name)
        
        # Add gateway-specific data formatting
        formatted_order_data = self._format_order_data(order_data, gateway_name)
        
        return gateway.create_payment_session(formatted_order_data)
    
    def verify_payment(self, payment_id: str, gateway_name: str) -> Dict[str, Any]:
        """
        Verify payment status with specified gateway
        
        Args:
            payment_id: Payment ID from gateway
            gateway_name: Payment gateway name
        
        Returns:
            Dict with payment verification details
        """
        gateway = self.get_gateway(gateway_name)
        return gateway.verify_payment(payment_id)
    
    def handle_webhook(self, payload: Dict[str, Any], gateway_name: str) -> Dict[str, Any]:
        """
        Handle webhook from specified gateway
        
        Args:
            payload: Webhook payload
            gateway_name: Payment gateway name
        
        Returns:
            Dict with webhook processing result
        """
        gateway = self.get_gateway(gateway_name)
        return gateway.handle_webhook(payload)
    
    def refund_payment(self, payment_id: str, amount: Decimal, gateway_name: str, reason: str = None) -> Dict[str, Any]:
        """
        Process refund through specified gateway
        
        Args:
            payment_id: Payment ID from gateway
            amount: Refund amount
            gateway_name: Payment gateway name
            reason: Refund reason
        
        Returns:
            Dict with refund details
        """
        gateway = self.get_gateway(gateway_name)
        return gateway.refund_payment(payment_id, amount, reason)
    
    def get_available_gateways(self) -> Dict[str, Any]:
        """
        Get list of available payment gateways
        
        Returns:
            Dict with available gateways and their capabilities
        """
        return {
            'TABBY': {
                'name': 'Tabby',
                'type': 'BNPL',
                'description': 'Buy Now, Pay Later - 4 installments',
                'supported_currencies': ['AED'],
                'min_amount': Decimal('50.00'),
                'max_amount': Decimal('10000.00'),
                'features': ['installments', 'no_interest', 'instant_approval']
            },
            'TAMARA': {
                'name': 'Tamara',
                'type': 'BNPL',
                'description': 'Buy Now, Pay Later - Flexible installments',
                'supported_currencies': ['AED'],
                'min_amount': Decimal('100.00'),
                'max_amount': Decimal('15000.00'),
                'features': ['flexible_installments', 'no_interest', 'instant_approval']
            },
            'ZIINA': {
                'name': 'Ziina',
                'type': 'INSTANT',
                'description': 'UAE Central Bank licensed instant payments with Apple Pay',
                'supported_currencies': ['AED'],
                'min_amount': Decimal('1.00'),
                'max_amount': Decimal('50000.00'),
                'features': ['apple_pay', 'instant_payment', 'refund_support', 'arabic_support']
            }
        }
    
    def get_suitable_gateways(self, amount: Decimal, customer_preference: str = None) -> list:
        """
        Get list of suitable payment gateways for given amount
        
        Args:
            amount: Payment amount
            customer_preference: Customer's preferred payment type
        
        Returns:
            List of suitable gateway names
        """
        available_gateways = self.get_available_gateways()
        suitable = []
        
        for gateway_name, gateway_info in available_gateways.items():
            # Check amount limits
            if amount < gateway_info['min_amount'] or amount > gateway_info['max_amount']:
                continue
            
            # Check customer preference
            if customer_preference:
                if customer_preference.upper() == 'BNPL' and gateway_info['type'] != 'BNPL':
                    continue
                elif customer_preference.upper() == 'INSTANT' and gateway_info['type'] != 'INSTANT':
                    continue
            
            suitable.append(gateway_name)
        
        return suitable
    
    def _format_order_data(self, order_data: Dict[str, Any], gateway_name: str) -> Dict[str, Any]:
        """
        Format order data for specific gateway requirements
        
        Args:
            order_data: Original order data
            gateway_name: Target gateway name
        
        Returns:
            Formatted order data
        """
        formatted_data = order_data.copy()
        
        if gateway_name == 'TABBY':
            # Tabby-specific formatting
            formatted_data['items'] = self._format_items_for_tabby(order_data.get('items', []))
            
        elif gateway_name == 'TAMARA':
            # Tamara-specific formatting
            formatted_data['items'] = self._format_items_for_tamara(order_data.get('items', []))
            
        elif gateway_name == 'ZIINA':
            # Ziina-specific formatting
            formatted_data['items'] = self._format_items_for_ziina(order_data.get('items', []))
        
        return formatted_data
    
    def _format_items_for_tabby(self, items: list) -> list:
        """Format items for Tabby API"""
        formatted_items = []
        for item in items:
            formatted_items.append({
                'title': item.get('name', 'Product'),
                'description': item.get('description', ''),
                'quantity': item.get('quantity', 1),
                'unit_price': str(item.get('price', 0)),
                'discount_amount': str(item.get('discount', 0)),
                'reference_id': item.get('product_id', ''),
                'image_url': item.get('image_url', ''),
                'product_url': item.get('product_url', ''),
                'category': item.get('category', 'chocolate')
            })
        return formatted_items
    
    def _format_items_for_tamara(self, items: list) -> list:
        """Format items for Tamara API"""
        formatted_items = []
        for item in items:
            formatted_items.append({
                'name': item.get('name', 'Product'),
                'sku': item.get('sku', ''),
                'quantity': item.get('quantity', 1),
                'unit_price': {
                    'amount': str(item.get('price', 0)),
                    'currency': 'AED'
                },
                'discount_amount': {
                    'amount': str(item.get('discount', 0)),
                    'currency': 'AED'
                },
                'image_url': item.get('image_url', ''),
                'product_url': item.get('product_url', ''),
                'category': item.get('category', 'chocolate')
            })
        return formatted_items
    
    def _format_items_for_ziina(self, items: list) -> list:
        """Format items for Ziina API"""
        formatted_items = []
        for item in items:
            formatted_items.append({
                'name': item.get('name', 'Product'),
                'description': item.get('description', ''),
                'quantity': item.get('quantity', 1),
                'unit_price': str(item.get('price', 0)),
                'total_price': str(item.get('price', 0) * item.get('quantity', 1)),
                'sku': item.get('sku', ''),
                'category': item.get('category', 'chocolate'),
                'image_url': item.get('image_url', ''),
                'product_url': item.get('product_url', '')
            })
        return formatted_items


# Global payment manager instance
payment_manager = PaymentManager()
