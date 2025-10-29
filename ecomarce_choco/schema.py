"""
Main GraphQL Schema
Combines all queries and mutations from different apps
"""
import graphene
from products.schema import ProductQuery, ProductMutation
from orders.schema import OrderQuery, OrderMutation
from users.schema import UserQuery, UserMutation

# Future imports for Phase 2 (Wholesale):
# from users.schema import UserQuery, UserMutation


class Query(
    UserQuery,
    ProductQuery,
    OrderQuery,
    graphene.ObjectType
):
    """
    Root Query - combines all queries from different apps
    
    Available Queries:
    - Products: products, product, categories, brands
    - Orders: cart, order
    """
    pass


class Mutation(
    UserMutation,
    ProductMutation,
    OrderMutation,
    graphene.ObjectType
):
    """
    Root Mutation - combines all mutations from different apps
    
    Available Mutations:
    - Products (Admin): createCategory, createBrand, createProduct, setProductPrice, updateInventory
    - Cart: addToCart, updateCartItem, removeFromCart, clearCart
    - Orders (Customer): createRetailOrder
    - Orders (Admin): updateOrderStatus, cancelOrder, updateShippingAddress
    """
    pass


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)

