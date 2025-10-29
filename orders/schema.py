"""
Orders GraphQL Schema
Handles cart, orders, and checkout
"""
import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from django.db import transaction
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import timedelta
import logging
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, OrderStatusHistory
from products.models import Product, ProductVariant

logger = logging.getLogger(__name__)


def _require_staff(info):
    user = info.context.user
    if not user.is_authenticated or not user.is_staff:
        raise Exception("Not authorized")

# ============================================================================
# GraphQL Types
# ============================================================================

class CartItemType(DjangoObjectType):
    """Cart Item object type - supports both regular products and variants"""
    subtotal = graphene.Decimal()
    product_name = graphene.String()
    display_name = graphene.String()
    variant_options_display = graphene.String()
    
    class Meta:
        model = CartItem
        fields = '__all__'
    
    def resolve_subtotal(self, info):
        return self.subtotal
    
    def resolve_product_name(self, info):
        return self.product.name if self.product else "Product not available"
    
    def resolve_display_name(self, info):
        """Full display name with variant info"""
        return self.display_name
    
    def resolve_variant_options_display(self, info):
        """Formatted variant options string (e.g., 'White, 500g')"""
        if self.variant:
            return ', '.join([vv.option_value.value for vv in self.variant.option_values.all()])
        return None


class CartType(DjangoObjectType):
    """Cart object type with computed totals"""
    items = graphene.List(CartItemType)
    total = graphene.Decimal()
    subtotal = graphene.Decimal()
    item_count = graphene.Int()
    tax_amount = graphene.Decimal()
    
    class Meta:
        model = Cart
        fields = '__all__'
    
    def resolve_items(self, info):
        return self.items.all().select_related('product', 'variant')
    
    def resolve_subtotal(self, info):
        return sum(item.subtotal for item in self.items.all())
    
    def resolve_tax_amount(self, info):
        """Calculate VAT (5% in UAE)"""
        subtotal = sum(item.subtotal for item in self.items.all())
        return subtotal * Decimal('0.05')
    
    def resolve_total(self, info):
        """Calculate total with VAT"""
        subtotal = sum(item.subtotal for item in self.items.all())
        tax = subtotal * Decimal('0.05')
        return subtotal + tax
    
    def resolve_item_count(self, info):
        return sum(item.quantity for item in self.items.all())


class ShippingAddressType(DjangoObjectType):
    """Shipping Address object type"""
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class OrderItemType(DjangoObjectType):
    """Order Item object type"""
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderStatusHistoryType(DjangoObjectType):
    """Order Status History object type"""
    class Meta:
        model = OrderStatusHistory
        fields = '__all__'


class OrderType(DjangoObjectType):
    """Order object type with related data"""
    items = graphene.List(OrderItemType)
    shipping_address = graphene.Field(ShippingAddressType)
    status_history = graphene.List(OrderStatusHistoryType)
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def resolve_items(self, info):
        return self.items.all()
    
    def resolve_shipping_address(self, info):
        try:
            return self.shipping_address
        except ShippingAddress.DoesNotExist:
            return None
    
    def resolve_status_history(self, info):
        return self.status_history.all()


# ============================================================================
# Input Types
# ============================================================================

class CustomerInput(graphene.InputObjectType):
    """Customer information input"""
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=True)
    company = graphene.String()


class AddressInput(graphene.InputObjectType):
    """Shipping address input"""
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


# ============================================================================
# Queries
# ============================================================================

class OrderQuery(graphene.ObjectType):
    """Order-related queries"""
    
    cart = graphene.Field(
        CartType, 
        session_key=graphene.String(required=True),
        description="Get cart by session key"
    )
    
    order = graphene.Field(
        OrderType, 
        order_number=graphene.String(required=True),
        description="Get order by order number"
    )
    
    orders = graphene.List(
        OrderType,
        status=graphene.String(description="Filter by order status"),
        order_type=graphene.String(description="Filter by order type"),
        limit=graphene.Int(description="Limit number of results"),
        description="Get list of all orders with optional filters"
    )
    
    def resolve_cart(self, info, session_key):
        """Get or create cart for session"""
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            defaults={'expires_at': timezone.now() + timedelta(days=2)}
        )
        return cart
    
    def resolve_order(self, info, order_number):
        """Get order by order number"""
        return Order.objects.filter(order_number=order_number).prefetch_related(
            'items__product',
            'items__variant',
            'shipping_address',
            'status_history'
        ).first()
    
    def resolve_orders(self, info, status=None, order_type=None, limit=None):
        """Get list of orders with optional filters"""
        queryset = Order.objects.all().order_by('-created_at')
        
        if status:
            queryset = queryset.filter(status=status)
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        
        if limit:
            queryset = queryset[:limit]
        
        # Optimize queries to avoid N+1
        return queryset.prefetch_related(
            'items__product',
            'items__variant',
            'shipping_address',
            'status_history'
        )


# ============================================================================
# Mutations
# ============================================================================

class AddToCart(graphene.Mutation):
    """Add product or variant to cart, or update quantity if already exists"""
    
    class Arguments:
        session_key = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        variant_id = graphene.Int(description="Variant ID if product has variants")
        quantity = graphene.Int(required=True)
    
    cart_item = graphene.Field(CartItemType)
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @transaction.atomic
    def mutate(self, info, session_key, product_id, quantity, variant_id=None):
        try:
            # Validate quantity
            if quantity <= 0:
                return AddToCart(
                    success=False, 
                    message="Quantity must be greater than 0"
                )
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                defaults={'expires_at': timezone.now() + timedelta(days=2)}
            )
            
            # Get product
            try:
                product = Product.objects.select_related('inventory').get(
                    id=product_id, 
                    is_active=True
                )
            except Product.DoesNotExist:
                return AddToCart(success=False, message="Product not found")
            
            # Handle variant if specified
            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)
                except ProductVariant.DoesNotExist:
                    return AddToCart(success=False, message="Variant not found")
            
            # Check if product has variants but no variant was specified
            if not variant_id and product.variants.exists():
                return AddToCart(
                    success=False, 
                    message="This product has variants. Please specify which variant to add."
                )
            
            # Determine stock and price based on whether it's a variant or regular product
            if variant:
                # Use variant stock and price
                if not variant.is_in_stock:
                    return AddToCart(success=False, message=f"Variant is out of stock")
                
                if variant.available_quantity < quantity:
                    return AddToCart(
                        success=False, 
                        message=f"Only {variant.available_quantity} items available"
                    )
                
                price_value = variant.effective_price
                display_name = f"{product.name} ({', '.join([vv.option_value.value for vv in variant.option_values.all()])})"
            else:
                # Use regular product stock and price
                if not hasattr(product, 'inventory'):
                    return AddToCart(success=False, message="Product inventory not set up")
                
                if not product.inventory.is_in_stock:
                    return AddToCart(success=False, message="Product is out of stock")
                
                if product.inventory.available_quantity < quantity:
                    return AddToCart(
                        success=False, 
                        message=f"Only {product.inventory.available_quantity} items available"
                    )
                
                # Get current retail price
                price = product.prices.filter(
                    price_type='RETAIL', 
                    is_active=True
                ).first()
                
                if not price:
                    return AddToCart(success=False, message="Price not available for this product")
                
                price_value = price.get_effective_price()
                display_name = product.name
            
            # Get or create cart item (unique by product + variant)
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={
                    'quantity': quantity,
                    'price_at_addition': price_value
                }
            )
            
            # If item already exists, update quantity
            if not item_created:
                new_quantity = cart_item.quantity + quantity
                
                # Check if new quantity exceeds available stock
                available = variant.available_quantity if variant else product.inventory.available_quantity
                if available < new_quantity:
                    return AddToCart(
                        success=False,
                        message=f"Cannot add {quantity} more. Only {available - cart_item.quantity} more available"
                    )
                
                cart_item.quantity = new_quantity
                cart_item.save()
                message = f"Updated cart: {display_name} quantity is now {new_quantity}"
            else:
                message = f"Added to cart: {display_name} x {quantity}"
            
            return AddToCart(
                cart_item=cart_item,
                cart=cart,
                success=True,
                message=message
            )
            
        except Product.DoesNotExist:
            return AddToCart(success=False, message="Product not found")
        except ProductVariant.DoesNotExist:
            return AddToCart(success=False, message="Product variant not found")
        except ValueError as e:
            logger.error(f"Value error adding to cart: {str(e)}")
            return AddToCart(success=False, message="Invalid data provided")
        except Exception as e:
            logger.error(f"Unexpected error adding to cart: {str(e)}", exc_info=True)
            return AddToCart(success=False, message="Unable to add to cart. Please try again.")


class UpdateCartItem(graphene.Mutation):
    """Update cart item quantity"""
    
    class Arguments:
        cart_item_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)
    
    cart_item = graphene.Field(CartItemType)
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @transaction.atomic
    def mutate(self, info, cart_item_id, quantity):
        try:
            cart_item = CartItem.objects.select_related('product__inventory', 'cart').get(
                id=cart_item_id
            )
            
            # If quantity is 0 or less, remove item
            if quantity <= 0:
                cart = cart_item.cart
                product_name = cart_item.product.name
                cart_item.delete()
                return UpdateCartItem(
                    cart=cart,
                    success=True,
                    message=f"Removed {product_name} from cart"
                )
            
            # Check if enough stock available
            if cart_item.product.inventory.available_quantity < quantity:
                return UpdateCartItem(
                    success=False,
                    message=f"Only {cart_item.product.inventory.available_quantity} items available"
                )
            
            # Update quantity
            cart_item.quantity = quantity
            cart_item.save()
            
            return UpdateCartItem(
                cart_item=cart_item,
                cart=cart_item.cart,
                success=True,
                message="Cart updated successfully"
            )
            
        except CartItem.DoesNotExist:
            return UpdateCartItem(success=False, message="Cart item not found")
        except ValueError as e:
            logger.error(f"Value error updating cart item: {str(e)}")
            return UpdateCartItem(success=False, message="Invalid quantity specified")
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}", exc_info=True)
            return UpdateCartItem(success=False, message="Unable to update cart item. Please try again.")


class RemoveFromCart(graphene.Mutation):
    """Remove item from cart"""
    
    class Arguments:
        cart_item_id = graphene.Int(required=True)
    
    cart = graphene.Field(CartType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, cart_item_id):
        try:
            cart_item = CartItem.objects.select_related('cart', 'product').get(
                id=cart_item_id
            )
            cart = cart_item.cart
            product_name = cart_item.product.name
            cart_item.delete()
            
            return RemoveFromCart(
                cart=cart,
                success=True,
                message=f"Removed {product_name} from cart"
            )
            
        except CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Cart item not found")
        except Exception as e:
            logger.error(f"Error removing from cart: {str(e)}", exc_info=True)
            return RemoveFromCart(success=False, message="Unable to remove item from cart. Please try again.")


class ClearCart(graphene.Mutation):
    """Clear all items from cart"""
    
    class Arguments:
        session_key = graphene.String(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, session_key):
        try:
            cart = Cart.objects.get(session_key=session_key)
            items_count = cart.items.count()
            cart.items.all().delete()
            
            return ClearCart(
                success=True,
                message=f"Cleared {items_count} items from cart"
            )
            
        except Cart.DoesNotExist:
            return ClearCart(success=False, message="Cart not found")
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}", exc_info=True)
            return ClearCart(success=False, message="Unable to clear cart. Please try again.")


class CreateRetailOrder(graphene.Mutation):
    """Create a retail order from cart"""
    
    class Arguments:
        session_key = graphene.String(required=True)
        customer_info = CustomerInput(required=True)
        shipping_address = AddressInput(required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @transaction.atomic
    def mutate(self, info, session_key, customer_info, shipping_address):
        try:
            # Get cart
            try:
                cart = Cart.objects.prefetch_related(
                    'items__product__inventory',
                    'items__variant'
                ).get(session_key=session_key)
            except Cart.DoesNotExist:
                return CreateRetailOrder(success=False, message="Cart not found")
            
            # Check if cart has items
            if not cart.items.exists():
                return CreateRetailOrder(success=False, message="Cart is empty")
            
            # Validate stock availability for all items
            for cart_item in cart.items.all():
                # Check variant stock if item has variant, otherwise check product stock
                if cart_item.variant:
                    if not cart_item.variant.is_in_stock:
                        return CreateRetailOrder(
                            success=False,
                            message=f"{cart_item.display_name} is out of stock"
                        )
                    
                    if cart_item.variant.available_quantity < cart_item.quantity:
                        return CreateRetailOrder(
                            success=False,
                            message=f"Not enough stock for {cart_item.display_name}. Only {cart_item.variant.available_quantity} available"
                        )
                else:
                    if not cart_item.product.inventory.is_in_stock:
                        return CreateRetailOrder(
                            success=False,
                            message=f"{cart_item.product.name} is out of stock"
                        )
                    
                    if cart_item.product.inventory.available_quantity < cart_item.quantity:
                        return CreateRetailOrder(
                            success=False,
                            message=f"Not enough stock for {cart_item.product.name}. Only {cart_item.product.inventory.available_quantity} available"
                        )
            
            # Calculate totals
            subtotal = sum(item.subtotal for item in cart.items.all())
            vat_rate = Decimal('0.05')  # 5% VAT in UAE
            tax_amount = (subtotal * vat_rate).quantize(Decimal('0.01'))
            
            # Delivery fee based on emirate (can be customized)
            delivery_fees = {
                'DUBAI': Decimal('15.00'),
                'ABU_DHABI': Decimal('20.00'),
                'SHARJAH': Decimal('18.00'),
                'AJMAN': Decimal('20.00'),
                'UMM_AL_QUWAIN': Decimal('25.00'),
                'RAS_AL_KHAIMAH': Decimal('25.00'),
                'FUJAIRAH': Decimal('30.00'),
            }
            delivery_fee = delivery_fees.get(shipping_address.emirate, Decimal('20.00'))
            
            total_amount = subtotal + tax_amount + delivery_fee
            
            # Create order
            order = Order.objects.create(
                order_type='RETAIL',
                status='PENDING',
                customer_name=customer_info.name,
                customer_email=customer_info.email,
                customer_phone=customer_info.phone,
                customer_company=customer_info.get('company', ''),
                subtotal=subtotal,
                tax_amount=tax_amount,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                currency='AED'
            )
            
            # Create order items (snapshot product data at time of purchase)
            for cart_item in cart.items.all():
                item_tax = (cart_item.subtotal * vat_rate).quantize(Decimal('0.01'))
                
                # Prepare variant options snapshot if variant exists
                variant_options_snapshot = None
                sku_to_use = cart_item.product.sku
                
                if cart_item.variant:
                    # Create variant options snapshot for historical record
                    variant_options_snapshot = {}
                    for vv in cart_item.variant.option_values.all():
                        variant_options_snapshot[vv.option_value.option.name] = vv.option_value.value
                    sku_to_use = cart_item.variant.sku
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    product_name=cart_item.display_name,
                    product_sku=sku_to_use,
                    variant_options=variant_options_snapshot,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price_at_addition,
                    tax_amount=item_tax,
                    total_price=cart_item.subtotal
                )
                
                # Reserve inventory (from variant or product)
                if cart_item.variant:
                    cart_item.variant.reserved_quantity += cart_item.quantity
                    cart_item.variant.save()
                else:
                    inventory = cart_item.product.inventory
                    inventory.reserved_quantity += cart_item.quantity
                    inventory.save()
            
            # Create shipping address
            ShippingAddress.objects.create(
                order=order,
                full_name=shipping_address.full_name,
                phone_number=shipping_address.phone_number,
                email=shipping_address.email,
                address_line1=shipping_address.address_line1,
                address_line2=shipping_address.get('address_line2', ''),
                city=shipping_address.city,
                emirate=shipping_address.emirate,
                area=shipping_address.get('area', ''),
                postal_code=shipping_address.get('postal_code', ''),
                delivery_instructions=shipping_address.get('delivery_instructions', '')
            )
            
            # Create initial status history
            OrderStatusHistory.objects.create(
                order=order,
                status='PENDING',
                notes='Order created'
            )
            
            # Clear cart
            cart.items.all().delete()
            
            return CreateRetailOrder(
                order=order,
                success=True,
                message=f"Order created successfully: {order.order_number}"
            )
            
        except Cart.DoesNotExist:
            return CreateRetailOrder(success=False, message="Cart not found")
        except IntegrityError as e:
            logger.error(f"Integrity error creating order: {str(e)}")
            return CreateRetailOrder(success=False, message="Failed to create order due to a data constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error creating order: {str(e)}")
            return CreateRetailOrder(success=False, message=f"Invalid order data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error creating retail order: {str(e)}", exc_info=True)
            return CreateRetailOrder(success=False, message="Failed to create order. Please try again.")


# ============================================================================
# Admin Mutations (Order Management)
# ============================================================================

class UpdateOrderStatusInput(graphene.InputObjectType):
    """Input for updating order status"""
    order_id = graphene.Int(required=True)
    status = graphene.String(required=True)
    notes = graphene.String()


class UpdateOrderStatus(graphene.Mutation):
    """Update order status (admin only)"""
    class Arguments:
        input = UpdateOrderStatusInput(required=True)
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            order = Order.objects.get(id=input.order_id)
            
            # Validate status
            valid_statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
            if input.status not in valid_statuses:
                return UpdateOrderStatus(
                    success=False, 
                    message=f"Invalid status. Valid options: {', '.join(valid_statuses)}"
                )
            
            old_status = order.status
            order.status = input.status
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=input.status,
                notes=input.get('notes', f'Status changed from {old_status} to {input.status}')
            )
            
            return UpdateOrderStatus(
                order=order,
                success=True,
                message=f"Order {order.order_number} status updated to {input.status}"
            )
            
        except Order.DoesNotExist:
            return UpdateOrderStatus(success=False, message="Order not found")
        except ValueError as e:
            logger.error(f"Value error updating order status: {str(e)}")
            return UpdateOrderStatus(success=False, message="Invalid status value provided")
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}", exc_info=True)
            return UpdateOrderStatus(success=False, message="Failed to update order status. Please try again.")


class CancelOrder(graphene.Mutation):
    """Cancel an order (admin only)"""
    class Arguments:
        order_id = graphene.Int(required=True)
        reason = graphene.String()
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, order_id, reason=None):
        _require_staff(info)
        try:
            order = Order.objects.get(id=order_id)
            
            # Check if order can be cancelled
            if order.status in ['DELIVERED', 'CANCELLED']:
                return CancelOrder(
                    success=False,
                    message=f"Cannot cancel order with status: {order.status}"
                )
            
            old_status = order.status
            order.status = 'CANCELLED'
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='CANCELLED',
                notes=reason or f'Order cancelled (was {old_status})'
            )
            
            # Return inventory to stock
            for item in order.items.all():
                if hasattr(item.product, 'inventory'):
                    inventory = item.product.inventory
                    inventory.quantity_in_stock += item.quantity
                    inventory.save()
            
            return CancelOrder(
                order=order,
                success=True,
                message=f"Order {order.order_number} cancelled successfully"
            )
            
        except Order.DoesNotExist:
            return CancelOrder(success=False, message="Order not found")
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}", exc_info=True)
            return CancelOrder(success=False, message="Failed to cancel order. Please try again.")


class UpdateShippingAddress(graphene.Mutation):
    """Update shipping address for an order (admin only)"""
    class Arguments:
        order_id = graphene.Int(required=True)
        full_name = graphene.String()
        phone_number = graphene.String()
        address_line1 = graphene.String()
        address_line2 = graphene.String()
        city = graphene.String()
        emirate = graphene.String()
        postal_code = graphene.String()
    
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, order_id, **kwargs):
        _require_staff(info)
        try:
            order = Order.objects.get(id=order_id)
            shipping = order.shipping_address
            
            # Update fields if provided
            if kwargs.get('full_name'):
                shipping.full_name = kwargs['full_name']
            if kwargs.get('phone_number'):
                shipping.phone_number = kwargs['phone_number']
            if kwargs.get('address_line1'):
                shipping.address_line1 = kwargs['address_line1']
            if kwargs.get('address_line2') is not None:
                shipping.address_line2 = kwargs['address_line2']
            if kwargs.get('city'):
                shipping.city = kwargs['city']
            if kwargs.get('emirate'):
                shipping.emirate = kwargs['emirate']
            if kwargs.get('postal_code') is not None:
                shipping.postal_code = kwargs['postal_code']
            
            shipping.save()
            
            # Log the change
            OrderStatusHistory.objects.create(
                order=order,
                status=order.status,
                notes='Shipping address updated'
            )
            
            return UpdateShippingAddress(
                order=order,
                success=True,
                message=f"Shipping address updated for order {order.order_number}"
            )
            
        except Order.DoesNotExist:
            return UpdateShippingAddress(success=False, message="Order not found")
        except ShippingAddress.DoesNotExist:
            return UpdateShippingAddress(success=False, message="Shipping address not found")
        except ValidationError as e:
            logger.error(f"Validation error updating shipping address: {str(e)}")
            return UpdateShippingAddress(success=False, message=f"Invalid address data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error updating shipping address: {str(e)}", exc_info=True)
            return UpdateShippingAddress(success=False, message="Failed to update shipping address. Please try again.")


# Admin Mutation class
class OrderAdminMutation(graphene.ObjectType):
    """All order admin mutations"""
    update_order_status = UpdateOrderStatus.Field()
    cancel_order = CancelOrder.Field()
    update_shipping_address = UpdateShippingAddress.Field()


# ============================================================================
# Mutation Class
# ============================================================================

class OrderMutation(OrderAdminMutation, graphene.ObjectType):
    """All order-related mutations"""
    # Customer mutations
    add_to_cart = AddToCart.Field()
    update_cart_item = UpdateCartItem.Field()
    remove_from_cart = RemoveFromCart.Field()
    clear_cart = ClearCart.Field()
    create_retail_order = CreateRetailOrder.Field()
    
    # Admin mutations inherited from OrderAdminMutation

