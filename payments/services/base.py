"""
Base payment service class
Common functionality for all payment gateways
"""
import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class BasePaymentService(ABC):
    """
    Abstract base class for payment services
    All payment gateways should inherit from this
    """
    
    def __init__(self):
        self.gateway_name = self.__class__.__name__
        self.logger = logger
    
    @abstractmethod
    def create_payment_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment session with the gateway
        Returns: {
            'success': bool,
            'payment_url': str,
            'payment_id': str,
            'expires_at': datetime,
            'error': str (if failed)
        }
        """
        pass
    
    @abstractmethod
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Verify payment status with the gateway
        Returns: {
            'success': bool,
            'status': str,
            'amount': Decimal,
            'transaction_id': str,
            'error': str (if failed)
        }
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook from payment gateway
        Returns: {
            'success': bool,
            'payment_id': str,
            'status': str,
            'amount': Decimal,
            'error': str (if failed)
        }
        """
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id: str, amount: Decimal, reason: str = None) -> Dict[str, Any]:
        """
        Process refund through the gateway
        Returns: {
            'success': bool,
            'refund_id': str,
            'amount': Decimal,
            'error': str (if failed)
        }
        """
        pass
    
    def format_amount(self, amount: Decimal) -> str:
        """Format amount for payment gateway (usually in smallest currency unit)"""
        # Convert AED to fils (1 AED = 100 fils)
        return str(int(amount * 100))
    
    def parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount from payment gateway response"""
        # Convert fils to AED
        return Decimal(amount_str) / 100
    
    def log_payment_event(self, event_type: str, data: Dict[str, Any]):
        """Log payment events for debugging and monitoring"""
        self.logger.info(f"[{self.gateway_name}] {event_type}: {data}")
    
    def validate_order_data(self, order_data: Dict[str, Any]) -> bool:
        """Validate order data before creating payment session"""
        required_fields = ['order_id', 'amount', 'currency', 'customer_email', 'customer_phone']
        
        for field in required_fields:
            if field not in order_data or not order_data[field]:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate amount
        if order_data['amount'] <= 0:
            self.logger.error("Invalid amount: must be greater than 0")
            return False
        
        # Validate currency
        if order_data['currency'] != 'AED':
            self.logger.error("Invalid currency: only AED supported")
            return False
        
        return True
    
    def get_expiry_time(self, minutes: int = 15) -> timezone.datetime:
        """Get payment session expiry time"""
        return timezone.now() + timedelta(minutes=minutes)
    
    def create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'gateway': self.gateway_name
        }
    
    def create_success_response(self, **kwargs) -> Dict[str, Any]:
        """Create standardized success response"""
        response = {
            'success': True,
            'gateway': self.gateway_name
        }
        response.update(kwargs)
        return response
