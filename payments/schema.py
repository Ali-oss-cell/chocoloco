"""
Payments GraphQL Schema
Handles payment gateway integration and processing
"""
import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from decimal import Decimal
from typing import Dict, Any

from .models import PaymentGateway, Payment, Refund, PaymentWebhook
from orders.models import Order
from .services.manager import payment_manager


# ============================================================================
# GraphQL Types
# ============================================================================

class PaymentGatewayType(DjangoObjectType):
    """Payment Gateway object type"""
    class Meta:
        model = PaymentGateway
        fields = '__all__'


class PaymentType(DjangoObjectType):
    """Payment object type"""
    class Meta:
        model = Payment
        fields = '__all__'


class RefundType(DjangoObjectType):
    """Refund object type"""
    class Meta:
        model = Refund
        fields = '__all__'


class PaymentWebhookType(DjangoObjectType):
    """Payment Webhook object type"""
    class Meta:
        model = PaymentWebhook
        fields = '__all__'


# ============================================================================
# Input Types
# ============================================================================

class PaymentItemInput(graphene.InputObjectType):
    """Input for payment item"""
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    quantity = graphene.Int(required=True)
    sku = graphene.String()


class ShippingAddressInput(graphene.InputObjectType):
    """Input for shipping address"""
    full_name = graphene.String(required=True)
    phone_number = graphene.String(required=True)
    email = graphene.String(required=True)
    address_line1 = graphene.String(required=True)
    address_line2 = graphene.String()
    city = graphene.String(required=True)
    emirate = graphene.String(required=True)
    area = graphene.String()
    postal_code = graphene.String()
    delivery_instructions = graphene.String()


class PaymentSessionInput(graphene.InputObjectType):
    """Input for creating payment session"""
    order_id = graphene.String(required=True)
    amount = graphene.Decimal(required=True)
    currency = graphene.String(default_value="AED")
    customer_email = graphene.String(required=True)
    customer_phone = graphene.String(required=True)
    customer_name = graphene.String()
    customer_id = graphene.String()
    tax_amount = graphene.Decimal(default_value=0)
    shipping_amount = graphene.Decimal(default_value=0)
    discount_amount = graphene.Decimal(default_value=0)
    items = graphene.List(PaymentItemInput)
    billing_address = graphene.Field(ShippingAddressInput)
    shipping_address = graphene.Field(ShippingAddressInput)


class PaymentVerificationInput(graphene.InputObjectType):
    """Input for verifying payment"""
    payment_id = graphene.String(required=True)
    gateway_name = graphene.String(required=True)


class RefundInput(graphene.InputObjectType):
    """Input for processing refund"""
    payment_id = graphene.String(required=True)
    amount = graphene.Decimal(required=True)
    gateway_name = graphene.String(required=True)
    reason = graphene.String()


# ============================================================================
# Queries
# ============================================================================

class PaymentQuery(graphene.ObjectType):
    """Payment-related queries"""
    
    payment_gateways = graphene.List(
        PaymentGatewayType,
        is_active=graphene.Boolean(),
        description="Get list of payment gateways"
    )
    
    payment = graphene.Field(
        PaymentType,
        id=graphene.Int(),
        payment_id=graphene.String(),
        description="Get payment by ID or payment ID"
    )
    
    payments = graphene.List(
        PaymentType,
        order_id=graphene.String(),
        status=graphene.String(),
        gateway=graphene.String(),
        description="Get list of payments with filters"
    )
    
    available_gateways = graphene.JSONString(
        amount=graphene.Decimal(),
        customer_preference=graphene.String(),
        description="Get available payment gateways for amount"
    )
    
    def resolve_payment_gateways(self, info, is_active=None):
        """Get payment gateways"""
        queryset = PaymentGateway.objects.all()
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset
    
    def resolve_payment(self, info, id=None, payment_id=None):
        """Get single payment"""
        if id:
            return Payment.objects.get(id=id)
        elif payment_id:
            return Payment.objects.get(payment_id=payment_id)
        return None
    
    def resolve_payments(self, info, order_id=None, status=None, gateway=None):
        """Get payments with filters"""
        queryset = Payment.objects.all()
        
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        if status:
            queryset = queryset.filter(status=status)
        if gateway:
            queryset = queryset.filter(gateway=gateway)
        
        return queryset.order_by('-created_at')
    
    def resolve_available_gateways(self, info, amount=None, customer_preference=None):
        """Get available payment gateways"""
        if amount:
            suitable_gateways = payment_manager.get_suitable_gateways(
                Decimal(str(amount)), 
                customer_preference
            )
            return {
                'suitable_gateways': suitable_gateways,
                'all_gateways': payment_manager.get_available_gateways()
            }
        else:
            return {
                'all_gateways': payment_manager.get_available_gateways()
            }


# ============================================================================
# Mutations
# ============================================================================

class CreatePaymentSession(graphene.Mutation):
    """Create payment session with gateway"""
    
    class Arguments:
        input = PaymentSessionInput(required=True)
        gateway_name = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    payment_url = graphene.String()
    payment_id = graphene.String()
    expires_at = graphene.DateTime()
    gateway_response = graphene.JSONString()
    
    def mutate(self, info, input, gateway_name):
        try:
            # Convert input to dict format expected by payment manager
            order_data = {
                'order_id': input.order_id,
                'amount': Decimal(str(input.amount)),
                'currency': input.currency,
                'customer_email': input.customer_email,
                'customer_phone': input.customer_phone,
                'customer_name': getattr(input, 'customer_name', None),
                'customer_id': getattr(input, 'customer_id', None),
                'tax_amount': Decimal(str(getattr(input, 'tax_amount', 0))),
                'shipping_amount': Decimal(str(getattr(input, 'shipping_amount', 0))),
                'discount_amount': Decimal(str(getattr(input, 'discount_amount', 0))),
            }
            
            # Convert items from input objects to dicts
            if hasattr(input, 'items') and input.items:
                order_data['items'] = [
                    {
                        'name': item.name,
                        'price': str(item.price),
                        'quantity': item.quantity,
                        'sku': getattr(item, 'sku', None)
                    }
                    for item in input.items
                ]
            else:
                order_data['items'] = []
            
            # Convert shipping address from input object to dict
            if hasattr(input, 'shipping_address') and input.shipping_address:
                addr = input.shipping_address
                order_data['shipping_address'] = {
                    'fullName': addr.full_name,
                    'phoneNumber': addr.phone_number,
                    'email': addr.email,
                    'addressLine1': addr.address_line1,
                    'addressLine2': getattr(addr, 'address_line2', None),
                    'city': addr.city,
                    'emirate': addr.emirate,
                    'area': getattr(addr, 'area', None),
                    'postalCode': getattr(addr, 'postal_code', None),
                    'deliveryInstructions': getattr(addr, 'delivery_instructions', None)
                }
            
            # Convert billing address if provided
            if hasattr(input, 'billing_address') and input.billing_address:
                addr = input.billing_address
                order_data['billing_address'] = {
                    'fullName': addr.full_name,
                    'phoneNumber': addr.phone_number,
                    'email': addr.email,
                    'addressLine1': addr.address_line1,
                    'addressLine2': getattr(addr, 'address_line2', None),
                    'city': addr.city,
                    'emirate': addr.emirate,
                    'area': getattr(addr, 'area', None),
                    'postalCode': getattr(addr, 'postal_code', None)
                }
            
            # Create payment session
            result = payment_manager.create_payment_session(order_data, gateway_name)
            
            if result['success']:
                # Get Order by order_number
                try:
                    order = Order.objects.get(order_number=order_data['order_id'])
                except Order.DoesNotExist:
                    return CreatePaymentSession(
                        success=False,
                        message=f"Order not found: {order_data['order_id']}",
                        payment_url=None,
                        payment_id=None,
                        expires_at=None,
                        gateway_response={}
                    )
                
                # Get PaymentGateway instance
                try:
                    payment_gateway = PaymentGateway.objects.get(name=gateway_name)
                except PaymentGateway.DoesNotExist:
                    # Create PaymentGateway if it doesn't exist (for development)
                    payment_gateway = PaymentGateway.objects.create(
                        name=gateway_name,
                        display_name=gateway_name.title(),
                        is_active=True,
                        is_test_mode=True,
                        api_key='',
                        api_secret='',
                        supported_currencies=['AED']
                    )
                
                # Save payment record to database
                payment = Payment.objects.create(
                    order=order,
                    payment_id=result['payment_id'],
                    gateway=payment_gateway,
                    payment_method='CREDIT_CARD',  # Default, can be updated later
                    amount=order_data['amount'],
                    currency=order_data['currency'],
                    status='PENDING',
                    gateway_response={
                        **result.get('gateway_response', {}),
                        'payment_url': result.get('payment_url'),
                        'expires_at': result.get('expires_at')
                    }
                )
                
                return CreatePaymentSession(
                    success=True,
                    message="Payment session created successfully",
                    payment_url=result['payment_url'],
                    payment_id=result['payment_id'],
                    expires_at=result['expires_at'],
                    gateway_response=result.get('gateway_response', {})
                )
            else:
                return CreatePaymentSession(
                    success=False,
                    message=result.get('error', 'Payment session creation failed'),
                    payment_url=None,
                    payment_id=None,
                    expires_at=None,
                    gateway_response=result
                )
                
        except Exception as e:
            return CreatePaymentSession(
                success=False,
                message=f"Error creating payment session: {str(e)}",
                payment_url=None,
                payment_id=None,
                expires_at=None,
                gateway_response={}
            )


class VerifyPayment(graphene.Mutation):
    """Verify payment status with gateway"""
    
    class Arguments:
        input = PaymentVerificationInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    status = graphene.String()
    amount = graphene.Decimal()
    transaction_id = graphene.String()
    gateway_response = graphene.JSONString()
    
    def mutate(self, info, input):
        try:
            # Verify payment with gateway
            result = payment_manager.verify_payment(
                input['payment_id'], 
                input['gateway_name']
            )
            
            if result['success']:
                # Update payment record
                try:
                    payment = Payment.objects.get(payment_id=input['payment_id'])
                    payment.status = result['status']
                    payment.transaction_id = result.get('transaction_id', '')
                    payment.gateway_response = result.get('gateway_response', {})
                    payment.verified_at = timezone.now()
                    payment.save()
                except Payment.DoesNotExist:
                    pass
                
                return VerifyPayment(
                    success=True,
                    message="Payment verified successfully",
                    status=result['status'],
                    amount=result['amount'],
                    transaction_id=result.get('transaction_id', ''),
                    gateway_response=result.get('gateway_response', {})
                )
            else:
                return VerifyPayment(
                    success=False,
                    message=result.get('error', 'Payment verification failed'),
                    status='unknown',
                    amount=Decimal('0'),
                    transaction_id='',
                    gateway_response=result
                )
                
        except Exception as e:
            return VerifyPayment(
                success=False,
                message=f"Error verifying payment: {str(e)}",
                status='error',
                amount=Decimal('0'),
                transaction_id='',
                gateway_response={}
            )


class ProcessRefund(graphene.Mutation):
    """Process refund through gateway"""
    
    class Arguments:
        input = RefundInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    refund_id = graphene.String()
    amount = graphene.Decimal()
    gateway_response = graphene.JSONString()
    
    def mutate(self, info, input):
        try:
            # Process refund through gateway
            result = payment_manager.refund_payment(
                input['payment_id'],
                Decimal(str(input['amount'])),
                input['gateway_name'],
                input.get('reason')
            )
            
            if result['success']:
                # Create refund record
                refund = Refund.objects.create(
                    payment_id=input['payment_id'],
                    refund_id=result['refund_id'],
                    gateway=input['gateway_name'],
                    amount=Decimal(str(input['amount'])),
                    reason=input.get('reason', 'Customer requested refund'),
                    status='processed',
                    gateway_response=result.get('gateway_response', {})
                )
                
                return ProcessRefund(
                    success=True,
                    message="Refund processed successfully",
                    refund_id=result['refund_id'],
                    amount=Decimal(str(input['amount'])),
                    gateway_response=result.get('gateway_response', {})
                )
            else:
                return ProcessRefund(
                    success=False,
                    message=result.get('error', 'Refund processing failed'),
                    refund_id='',
                    amount=Decimal('0'),
                    gateway_response=result
                )
                
        except Exception as e:
            return ProcessRefund(
                success=False,
                message=f"Error processing refund: {str(e)}",
                refund_id='',
                amount=Decimal('0'),
                gateway_response={}
            )


class HandleWebhook(graphene.Mutation):
    """Handle webhook from payment gateway"""
    
    class Arguments:
        payload = graphene.JSONString(required=True)
        gateway_name = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    payment_id = graphene.String()
    status = graphene.String()
    amount = graphene.Decimal()
    
    def mutate(self, info, payload, gateway_name):
        try:
            # Handle webhook
            result = payment_manager.handle_webhook(payload, gateway_name)
            
            if result['success']:
                # Log webhook
                webhook = PaymentWebhook.objects.create(
                    gateway=gateway_name,
                    payload=payload,
                    payment_id=result['payment_id'],
                    status=result['status'],
                    amount=result['amount'],
                    processed_at=timezone.now()
                )
                
                # Update payment if exists
                try:
                    payment = Payment.objects.get(payment_id=result['payment_id'])
                    payment.status = result['status']
                    payment.gateway_response = payload
                    payment.save()
                except Payment.DoesNotExist:
                    pass
                
                return HandleWebhook(
                    success=True,
                    message="Webhook processed successfully",
                    payment_id=result['payment_id'],
                    status=result['status'],
                    amount=result['amount']
                )
            else:
                return HandleWebhook(
                    success=False,
                    message=result.get('error', 'Webhook processing failed'),
                    payment_id='',
                    status='error',
                    amount=Decimal('0')
                )
                
        except Exception as e:
            return HandleWebhook(
                success=False,
                message=f"Error processing webhook: {str(e)}",
                payment_id='',
                status='error',
                amount=Decimal('0')
            )


# ============================================================================
# Mutation Classes
# ============================================================================

class PaymentMutation(graphene.ObjectType):
    """Payment mutations"""
    create_payment_session = CreatePaymentSession.Field()
    verify_payment = VerifyPayment.Field()
    process_refund = ProcessRefund.Field()
    handle_webhook = HandleWebhook.Field()
