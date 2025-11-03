"""
Products GraphQL Schema
Handles all product-related queries and admin mutations
"""
import graphene
from graphene_django import DjangoObjectType
from django.db import models
from django.db.models import Case, When, Value, IntegerField
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
import io
import logging
from decimal import Decimal

from .models import (
    Product, Category, Brand, 
    ProductImage, ProductImageUseCase, ProductPrice, Inventory, ProductReview,
    ProductVariant, ProductVariantOption, ProductVariantOptionValue, ProductVariantValue
)

logger = logging.getLogger(__name__)


def _require_staff(info):
    user = info.context.user
    if not user.is_authenticated or not user.is_staff:
        raise Exception("Not authorized")


# ============================================================================
# GraphQL Types (Object Types)
# ============================================================================

class CategoryType(DjangoObjectType):
    """Category object type"""
    class Meta:
        model = Category
        fields = '__all__'


class BrandType(DjangoObjectType):
    """Brand object type"""
    class Meta:
        model = Brand
        fields = '__all__'


class ProductImageType(DjangoObjectType):
    """Product Image object type"""
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductImageUseCaseType(DjangoObjectType):
    """Product Use Case Image object type"""
    class Meta:
        model = ProductImageUseCase
        fields = '__all__'


class ProductPriceType(DjangoObjectType):
    """Product Price object type"""
    effective_price = graphene.Decimal()
    
    class Meta:
        model = ProductPrice
        fields = '__all__'
    
    def resolve_effective_price(self, info):
        """Return sale price if available, otherwise base price"""
        return self.get_effective_price()


class InventoryType(DjangoObjectType):
    """Inventory object type with computed fields"""
    available_quantity = graphene.Int()
    is_in_stock = graphene.Boolean()
    is_low_stock = graphene.Boolean()
    
    class Meta:
        model = Inventory
        fields = '__all__'
    
    def resolve_available_quantity(self, info):
        return self.available_quantity
    
    def resolve_is_in_stock(self, info):
        return self.is_in_stock
    
    def resolve_is_low_stock(self, info):
        return self.is_low_stock


class ProductReviewType(DjangoObjectType):
    """Product Review object type"""
    class Meta:
        model = ProductReview
        fields = '__all__'


class ProductVariantOptionValueType(DjangoObjectType):
    """Product Variant Option Value object type"""
    class Meta:
        model = ProductVariantOptionValue
        fields = '__all__'


class ProductVariantOptionType(DjangoObjectType):
    """Product Variant Option object type"""
    values = graphene.List(ProductVariantOptionValueType)
    
    class Meta:
        model = ProductVariantOption
        fields = '__all__'
    
    def resolve_values(self, info):
        return self.values.all()


class ProductVariantType(DjangoObjectType):
    """Product Variant object type"""
    available_quantity = graphene.Int()
    is_in_stock = graphene.Boolean()
    is_low_stock = graphene.Boolean()
    effective_price = graphene.Decimal()
    option_values = graphene.List(ProductVariantOptionValueType)
    
    class Meta:
        model = ProductVariant
        fields = '__all__'
    
    def resolve_available_quantity(self, info):
        return self.available_quantity
    
    def resolve_is_in_stock(self, info):
        return self.is_in_stock
    
    def resolve_is_low_stock(self, info):
        return self.is_low_stock
    
    def resolve_effective_price(self, info):
        return self.effective_price
    
    def resolve_option_values(self, info):
        return [vv.option_value for vv in self.option_values.all()]


class ProductType(DjangoObjectType):
    """
    Product object type with related data
    Includes: images, use case images, prices, inventory, and computed fields
    """
    images = graphene.List(ProductImageType)
    usecase_images = graphene.List(ProductImageUseCaseType)
    prices = graphene.List(ProductPriceType)
    inventory = graphene.Field(InventoryType)
    reviews = graphene.List(ProductReviewType)
    retail_price = graphene.Decimal()
    in_stock = graphene.Boolean()
    average_rating = graphene.Float()
    
    # Variants
    variant_options = graphene.List(ProductVariantOptionType)
    variants = graphene.List(ProductVariantType)
    has_variants = graphene.Boolean()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def resolve_images(self, info):
        """Get all product images ordered by display order"""
        return self.images.all().order_by('display_order')
    
    def resolve_usecase_images(self, info):
        """Get all use case images ordered by display order"""
        return self.usecase_images.all().order_by('display_order')
    
    def resolve_prices(self, info):
        """Get only active prices"""
        return self.prices.filter(is_active=True)
    
    def resolve_inventory(self, info):
        """Get product inventory"""
        try:
            return self.inventory
        except Inventory.DoesNotExist:
            return None
    
    def resolve_reviews(self, info):
        """Get only approved reviews"""
        return self.reviews.filter(is_approved=True)
    
    def resolve_retail_price(self, info):
        """Get current retail price (with sale price if applicable)"""
        price = self.prices.filter(
            price_type='RETAIL', 
            is_active=True
        ).first()
        return price.get_effective_price() if price else None
    
    def resolve_in_stock(self, info):
        """Check if product is in stock"""
        try:
            return self.inventory.is_in_stock
        except (Inventory.DoesNotExist, AttributeError):
            return False
    
    def resolve_average_rating(self, info):
        """Calculate average rating from approved reviews"""
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            avg = approved_reviews.aggregate(avg=models.Avg('rating'))['avg']
            return float(avg) if avg else None
        return None
    
    def resolve_variant_options(self, info):
        """Get all variant options for this product"""
        return self.variant_options.all().order_by('display_order')
    
    def resolve_variants(self, info):
        """Get all active variants for this product"""
        return self.variants.filter(is_active=True).order_by('-is_default', 'sku')
    
    def resolve_has_variants(self, info):
        """Check if product has variants"""
        return self.variants.exists()


# ============================================================================
# Queries
# ============================================================================

class ProductQuery(graphene.ObjectType):
    """
    All product-related queries
    """
    
    # Single product queries
    product = graphene.Field(
        ProductType, 
        id=graphene.Int(), 
        slug=graphene.String(),
        description="Get a single product by ID or slug"
    )
    
    # List of products with filters
    products = graphene.List(
        ProductType,
        category=graphene.String(description="Filter by category slug"),
        brand=graphene.String(description="Filter by brand slug"),
        search=graphene.String(description="Search in name, description, or SKU"),
        in_stock=graphene.Boolean(description="Filter by stock availability"),
        featured=graphene.Boolean(description="Filter featured products"),
        min_price=graphene.Decimal(description="Minimum price filter"),
        max_price=graphene.Decimal(description="Maximum price filter"),
        sort_by=graphene.String(description="Sort by: name, price_asc, price_desc, rating, newest, oldest"),
        limit=graphene.Int(description="Limit number of results"),
        description="Get list of products with optional filters and sorting"
    )
    
    # Search autocomplete - optimized for fast results as user types
    search_products = graphene.List(
        ProductType,
        query=graphene.String(required=True, description="Search query"),
        limit=graphene.Int(description="Maximum number of results (default: 10)"),
        sort_by=graphene.String(description="Sort by: name, price_asc, price_desc, rating, newest, oldest"),
        description="Fast product search for autocomplete - searches name, SKU, description, brand, category"
    )
    
    # Fuzzy search with typo tolerance
    fuzzy_search_products = graphene.List(
        ProductType,
        query=graphene.String(required=True, description="Search query with typo tolerance"),
        limit=graphene.Int(description="Maximum number of results (default: 10)"),
        typo_tolerance=graphene.Int(description="Number of character differences allowed (default: 2)"),
        sort_by=graphene.String(description="Sort by: name, price_asc, price_desc, rating, newest, oldest"),
        description="Fuzzy search that handles typos and misspellings - finds closest matches"
    )
    
    # Smart search suggestions
    search_suggestions = graphene.List(
        graphene.String,
        query=graphene.String(required=True, description="Search query to get suggestions for"),
        limit=graphene.Int(description="Maximum number of suggestions (default: 5)"),
        description="Get search suggestions based on popular searches and product names"
    )
    
    # Categories
    categories = graphene.List(
        CategoryType, 
        parent_id=graphene.Int(description="Filter by parent category"),
        description="Get list of categories"
    )
    
    category = graphene.Field(
        CategoryType, 
        id=graphene.Int(), 
        slug=graphene.String(),
        description="Get a single category by ID or slug"
    )
    
    # Brands
    brands = graphene.List(
        BrandType, 
        is_active=graphene.Boolean(description="Filter by active status"),
        description="Get list of brands"
    )
    
    brand = graphene.Field(
        BrandType, 
        id=graphene.Int(), 
        slug=graphene.String(),
        description="Get a single brand by ID or slug"
    )
    
    # ========================================================================
    # Resolvers
    # ========================================================================
    
    def resolve_product(self, info, id=None, slug=None):
        """
        Get a single product by ID or slug
        PUBLIC ENDPOINT - No authentication required
        """
        queryset = Product.objects.filter(is_active=True)
        
        if id:
            queryset = queryset.filter(id=id)
        elif slug:
            queryset = queryset.filter(slug=slug)
        else:
            return None
        
        # Optimize queries to avoid N+1
        return queryset.select_related(
            'brand', 
            'category', 
            'inventory'
        ).prefetch_related(
            'images',
            'usecase_images',
            'prices',
            'variants',
            'variant_options__values'
        ).first()
    
    def resolve_products(self, info, category=None, brand=None, search=None, 
                        in_stock=None, featured=None, min_price=None, max_price=None,
                        sort_by=None, limit=None):
        """
        Get list of products with optional filters and sorting
        PUBLIC ENDPOINT - No authentication required
        Optimized with select_related and prefetch_related
        """
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by brand
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        # Search filter
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(sku__icontains=search)
            )
        
        # Stock filter
        if in_stock is not None:
            if in_stock:
                queryset = queryset.filter(
                    inventory__quantity_in_stock__gt=models.F('inventory__reserved_quantity')
                )
        
        # Featured filter
        if featured is not None:
            queryset = queryset.filter(featured=featured)
        
        # Price filters (only retail prices)
        if min_price is not None or max_price is not None:
            price_filter = models.Q(prices__price_type='RETAIL', prices__is_active=True)
            
            if min_price is not None:
                price_filter &= models.Q(prices__base_price__gte=min_price)
            
            if max_price is not None:
                price_filter &= models.Q(prices__base_price__lte=max_price)
            
            queryset = queryset.filter(price_filter).distinct()
        
        # Apply sorting
        if sort_by:
            if sort_by == 'name':
                queryset = queryset.order_by('name')
            elif sort_by == 'price_asc':
                queryset = queryset.order_by('prices__base_price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-prices__base_price')
            elif sort_by == 'rating':
                # Sort by average rating (if reviews exist)
                queryset = queryset.order_by('-reviews__rating')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'oldest':
                queryset = queryset.order_by('created_at')
        else:
            # Default sorting by name
            queryset = queryset.order_by('name')
        
        # Apply limit if specified
        if limit:
            queryset = queryset[:limit]
        
        # Optimize queries
        return queryset.select_related('brand', 'category', 'inventory').prefetch_related(
            'images', 
            'usecase_images',
            'prices',
            'variants',
            'variant_options__values'
        )
    
    def resolve_categories(self, info, parent_id=None):
        """
        Get list of categories, optionally filtered by parent
        PUBLIC ENDPOINT - No authentication required
        """
        queryset = Category.objects.filter(is_active=True)
        
        if parent_id is not None:
            queryset = queryset.filter(parent_category_id=parent_id)
        
        return queryset.order_by('display_order', 'name')
    
    def resolve_category(self, info, id=None, slug=None):
        """
        Get a single category by ID or slug
        PUBLIC ENDPOINT - No authentication required
        """
        if id:
            return Category.objects.filter(id=id, is_active=True).first()
        if slug:
            return Category.objects.filter(slug=slug, is_active=True).first()
        return None
    
    def resolve_brands(self, info, is_active=None):
        """
        Get list of brands, optionally filtered by active status
        PUBLIC ENDPOINT - No authentication required
        """
        queryset = Brand.objects.all()
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('display_order', 'name')
    
    def resolve_brand(self, info, id=None, slug=None):
        """Get a single brand by ID or slug"""
        if id:
            return Brand.objects.filter(id=id, is_active=True).first()
        if slug:
            return Brand.objects.filter(slug=slug, is_active=True).first()
        return None
    
    def resolve_search_products(self, info, query, limit=10, sort_by=None):
        """
        Fast search for autocomplete/search-as-you-type
        
        Searches across multiple fields:
        - Product name (highest priority)
        - Product SKU
        - Product description
        - Brand name
        - Category name
        
        Returns limited results sorted by relevance
        """
        if not query or len(query) < 2:
            # Require at least 2 characters for search
            return Product.objects.none()
        
        # Build search query using OR conditions
        search_query = (
            models.Q(name__icontains=query) |  # Search in product name
            models.Q(sku__icontains=query) |  # Search in SKU
            models.Q(description__icontains=query) |  # Search in description
            models.Q(brand__name__icontains=query) |  # Search in brand name
            models.Q(category__name__icontains=query)  # Search in category name
        )
        
        # Get products matching search
        queryset = Product.objects.filter(
            search_query,
            is_active=True
        ).select_related(
            'brand', 
            'category', 
            'inventory'
        ).prefetch_related(
            'images',
            'usecase_images',
            'prices'
        )
        
        # Apply sorting
        if sort_by:
            if sort_by == 'name':
                queryset = queryset.order_by('name')
            elif sort_by == 'price_asc':
                queryset = queryset.order_by('prices__base_price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-prices__base_price')
            elif sort_by == 'rating':
                queryset = queryset.order_by('-reviews__rating')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'oldest':
                queryset = queryset.order_by('created_at')
        else:
            # Default: prioritize products where name starts with the query
            # This gives better results for autocomplete
            queryset = queryset.annotate(
                name_priority=Case(
                    When(name__istartswith=query, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            ).order_by('name_priority', 'name')
        
        # Limit results for fast response
        return queryset[:limit]
    
    def resolve_fuzzy_search_products(self, info, query, limit=10, typo_tolerance=2, sort_by=None):
        """
        Fuzzy search with typo tolerance
        
        Uses Levenshtein distance to find products even with typos.
        Searches across multiple fields and ranks by similarity.
        """
        if not query or len(query) < 2:
            return Product.objects.none()
        
        from difflib import SequenceMatcher
        
        # Get all products for fuzzy matching
        all_products = Product.objects.filter(is_active=True).select_related(
            'brand', 'category', 'inventory'
        ).prefetch_related('images', 'prices')
        
        # Calculate similarity scores for each product
        product_scores = []
        
        for product in all_products:
            max_similarity = 0.0
            
            # Check similarity against multiple fields
            fields_to_check = [
                product.name.lower(),
                product.sku.lower(),
                product.brand.name.lower() if product.brand else '',
                product.category.name.lower() if product.category else '',
                product.description.lower() if product.description else ''
            ]
            
            for field in fields_to_check:
                if field:
                    # Calculate similarity ratio (0.0 to 1.0)
                    similarity = SequenceMatcher(None, query.lower(), field).ratio()
                    max_similarity = max(max_similarity, similarity)
            
            # Only include products with reasonable similarity
            # Adjust threshold based on query length
            min_threshold = 0.3 if len(query) <= 3 else 0.4
            
            if max_similarity >= min_threshold:
                product_scores.append((product, max_similarity))
        
        # Apply additional sorting if requested
        if sort_by:
            if sort_by == 'name':
                product_scores.sort(key=lambda x: (x[0].name, -x[1]), reverse=False)
            elif sort_by == 'price_asc':
                product_scores.sort(key=lambda x: (x[0].prices.filter(is_active=True).first().base_price if x[0].prices.filter(is_active=True).exists() else 0, -x[1]), reverse=False)
            elif sort_by == 'price_desc':
                product_scores.sort(key=lambda x: (x[0].prices.filter(is_active=True).first().base_price if x[0].prices.filter(is_active=True).exists() else 0, -x[1]), reverse=True)
            elif sort_by == 'rating':
                product_scores.sort(key=lambda x: (x[0].reviews.filter(is_approved=True).aggregate(avg=models.Avg('rating'))['avg'] or 0, -x[1]), reverse=True)
            elif sort_by == 'newest':
                product_scores.sort(key=lambda x: (x[0].created_at, -x[1]), reverse=True)
            elif sort_by == 'oldest':
                product_scores.sort(key=lambda x: (x[0].created_at, -x[1]), reverse=False)
        else:
            # Default: sort by similarity score (highest first)
            product_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return [product for product, score in product_scores[:limit]]
    
    def resolve_search_suggestions(self, info, query, limit=5):
        """
        Provide smart search suggestions based on the query
        
        Returns suggestions that help users find what they're looking for
        even if they don't know the exact spelling or name.
        """
        if not query or len(query) < 2:
            return []
        
        from difflib import get_close_matches
        
        # Get all unique product names, brand names, and category names
        all_names = set()
        
        # Add product names
        for product in Product.objects.filter(is_active=True).values_list('name', flat=True):
            all_names.add(product.lower())
        
        # Add brand names
        for brand in Brand.objects.filter(is_active=True).values_list('name', flat=True):
            all_names.add(brand.lower())
        
        # Add category names
        for category in Category.objects.filter(is_active=True).values_list('name', flat=True):
            all_names.add(category.lower())
        
        # Find close matches
        suggestions = get_close_matches(
            query.lower(), 
            list(all_names), 
            n=limit, 
            cutoff=0.3
        )
        
        # If no close matches, provide popular search terms
        if not suggestions:
            popular_terms = [
                'chocolate', 'dark chocolate', 'milk chocolate', 'white chocolate',
                'lindt', 'godiva', 'ferrero rocher', 'toblerone', 'cadbury',
                'truffles', 'gift box', 'premium chocolates'
            ]
            
            # Find terms that contain the query
            for term in popular_terms:
                if query.lower() in term.lower():
                    suggestions.append(term)
                    if len(suggestions) >= limit:
                        break
        
        return suggestions[:limit]


# ============================================================================
# Admin Mutations (Product Management)
# ============================================================================

# Input Types for Admin
class CategoryInput(graphene.InputObjectType):
    """Input for creating/updating categories"""
    name = graphene.String(required=True)
    slug = graphene.String()
    description = graphene.String()
    parent_category_id = graphene.Int()
    is_active = graphene.Boolean()
    display_order = graphene.Int()


class BrandInput(graphene.InputObjectType):
    """Input for creating/updating brands"""
    name = graphene.String(required=True)
    slug = graphene.String()
    description = graphene.String()
    country_of_origin = graphene.String()
    is_active = graphene.Boolean()
    display_order = graphene.Int()


class ProductInput(graphene.InputObjectType):
    """Input for creating/updating products"""
    sku = graphene.String()
    name = graphene.String(required=True)
    slug = graphene.String()
    brand_id = graphene.Int(required=True)
    category_id = graphene.Int(required=True)
    description = graphene.String()
    short_description = graphene.String()
    ingredients = graphene.String()
    allergen_info = graphene.String()
    weight = graphene.Decimal()
    volume = graphene.Decimal()
    unit_type = graphene.String()
    is_active = graphene.Boolean()
    featured = graphene.Boolean()


class ProductPriceInput(graphene.InputObjectType):
    """Input for setting product prices"""
    product_id = graphene.Int(required=True)
    price_type = graphene.String(required=True)  # RETAIL or WHOLESALE
    base_price = graphene.Decimal(required=True)
    sale_price = graphene.Decimal()
    min_quantity = graphene.Int()
    is_active = graphene.Boolean()


class InventoryInput(graphene.InputObjectType):
    """Input for updating inventory"""
    product_id = graphene.Int(required=True)
    quantity_in_stock = graphene.Int(required=True)
    low_stock_threshold = graphene.Int()
    warehouse_location = graphene.String()


class ProductImageInput(graphene.InputObjectType):
    """Input for uploading product images"""
    product_id = graphene.Int(required=True)
    image = graphene.String(required=True, description="Base64 encoded image data")
    alt_text = graphene.String()
    is_primary = graphene.Boolean(default_value=False)
    display_order = graphene.Int(default_value=0)


class ProductImageUseCaseInput(graphene.InputObjectType):
    """Input for uploading product use case images"""
    product_id = graphene.Int(required=True)
    image = graphene.String(required=True, description="Base64 encoded image data")
    usecase_type = graphene.String(required=True, description="Type of use case (BREAKFAST, DESSERT, GIFT, etc.)")
    title = graphene.String(required=True, description="Short title for this use case")
    description = graphene.String(description="Description of how product is used")
    alt_text = graphene.String()
    display_order = graphene.Int(required=True, description="Display order (1-4)")


# Admin Mutations
class CreateCategory(graphene.Mutation):
    """Create a new category"""
    class Arguments:
        input = CategoryInput(required=True)
    
    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            category = Category.objects.create(
                name=input.name,
                slug=input.get('slug', ''),
                description=input.get('description', ''),
                parent_category_id=input.get('parent_category_id'),
                is_active=input.get('is_active', True),
                display_order=input.get('display_order', 0)
            )
            return CreateCategory(
                category=category,
                success=True,
                message=f"Category '{category.name}' created successfully"
            )
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'slug' in error_str:
                return CreateCategory(success=False, message="A category with this slug already exists")
            logger.error(f"Integrity error creating category: {str(e)}")
            return CreateCategory(success=False, message="Failed to create category due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error creating category: {str(e)}")
            return CreateCategory(success=False, message=f"Invalid category data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}", exc_info=True)
            return CreateCategory(success=False, message="Failed to create category. Please try again.")


class UpdateCategory(graphene.Mutation):
    """Update an existing category"""
    class Arguments:
        id = graphene.Int(required=True)
        input = CategoryInput(required=True)
    
    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, input):
        _require_staff(info)
        try:
            category = Category.objects.get(id=id)
            
            category.name = input.name
            if input.get('slug'):
                category.slug = input.slug
            if input.get('description') is not None:
                category.description = input.description
            if input.get('parent_category_id') is not None:
                category.parent_category_id = input.parent_category_id
            if input.get('is_active') is not None:
                category.is_active = input.is_active
            if input.get('display_order') is not None:
                category.display_order = input.display_order
            
            category.save()
            
            return UpdateCategory(
                category=category,
                success=True,
                message=f"Category '{category.name}' updated successfully"
            )
        except Category.DoesNotExist:
            return UpdateCategory(success=False, message="Category not found")
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'slug' in error_str:
                return UpdateCategory(success=False, message="A category with this slug already exists")
            logger.error(f"Integrity error updating category: {str(e)}")
            return UpdateCategory(success=False, message="Failed to update category due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error updating category: {str(e)}")
            return UpdateCategory(success=False, message=f"Invalid category data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}", exc_info=True)
            return UpdateCategory(success=False, message="Failed to update category. Please try again.")


class CreateBrand(graphene.Mutation):
    """Create a new brand"""
    class Arguments:
        input = BrandInput(required=True)
    
    brand = graphene.Field(BrandType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            brand = Brand.objects.create(
                name=input.name,
                slug=input.get('slug', ''),
                description=input.get('description', ''),
                country_of_origin=input.get('country_of_origin', ''),
                is_active=input.get('is_active', True),
                display_order=input.get('display_order', 0)
            )
            return CreateBrand(
                brand=brand,
                success=True,
                message=f"Brand '{brand.name}' created successfully"
            )
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'slug' in error_str:
                return CreateBrand(success=False, message="A brand with this slug already exists")
            logger.error(f"Integrity error creating brand: {str(e)}")
            return CreateBrand(success=False, message="Failed to create brand due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error creating brand: {str(e)}")
            return CreateBrand(success=False, message=f"Invalid brand data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error creating brand: {str(e)}", exc_info=True)
            return CreateBrand(success=False, message="Failed to create brand. Please try again.")


class UpdateBrand(graphene.Mutation):
    """Update an existing brand"""
    class Arguments:
        id = graphene.Int(required=True)
        input = BrandInput(required=True)
    
    brand = graphene.Field(BrandType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, input):
        _require_staff(info)
        try:
            brand = Brand.objects.get(id=id)
            
            brand.name = input.name
            if input.get('slug'):
                brand.slug = input.slug
            if input.get('description') is not None:
                brand.description = input.description
            if input.get('country_of_origin') is not None:
                brand.country_of_origin = input.country_of_origin
            if input.get('is_active') is not None:
                brand.is_active = input.is_active
            if input.get('display_order') is not None:
                brand.display_order = input.display_order
            
            brand.save()
            
            return UpdateBrand(
                brand=brand,
                success=True,
                message=f"Brand '{brand.name}' updated successfully"
            )
        except Brand.DoesNotExist:
            return UpdateBrand(success=False, message="Brand not found")
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'slug' in error_str:
                return UpdateBrand(success=False, message="A brand with this slug already exists")
            logger.error(f"Integrity error updating brand: {str(e)}")
            return UpdateBrand(success=False, message="Failed to update brand due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error updating brand: {str(e)}")
            return UpdateBrand(success=False, message=f"Invalid brand data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error updating brand: {str(e)}", exc_info=True)
            return UpdateBrand(success=False, message="Failed to update brand. Please try again.")


class CreateProduct(graphene.Mutation):
    """Create a new product"""
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            # Validate brand and category exist
            brand = Brand.objects.get(id=input.brand_id)
            category = Category.objects.get(id=input.category_id)
            
            product = Product.objects.create(
                sku=input.get('sku', ''),
                name=input.name,
                slug=input.get('slug', ''),
                brand=brand,
                category=category,
                description=input.get('description', ''),
                short_description=input.get('short_description', ''),
                ingredients=input.get('ingredients', ''),
                allergen_info=input.get('allergen_info', ''),
                weight=input.get('weight'),
                volume=input.get('volume'),
                unit_type=input.get('unit_type', 'PIECE'),
                is_active=input.get('is_active', True),
                featured=input.get('featured', False)
            )
            
            # Auto-create inventory record
            Inventory.objects.create(
                product=product,
                quantity_in_stock=0,
                low_stock_threshold=10
            )
            
            return CreateProduct(
                product=product,
                success=True,
                message=f"Product '{product.name}' created successfully"
            )
        except (Brand.DoesNotExist, Category.DoesNotExist) as e:
            return CreateProduct(success=False, message="Brand or Category not found")
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'sku' in error_str:
                return CreateProduct(success=False, message="A product with this SKU already exists")
            elif 'slug' in error_str:
                return CreateProduct(success=False, message="A product with this slug already exists")
            logger.error(f"Integrity error creating product: {str(e)}")
            return CreateProduct(success=False, message="Failed to create product due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error creating product: {str(e)}")
            return CreateProduct(success=False, message=f"Invalid product data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}", exc_info=True)
            return CreateProduct(success=False, message="Failed to create product. Please try again.")


class UpdateProduct(graphene.Mutation):
    """Update an existing product"""
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, input):
        _require_staff(info)
        try:
            product = Product.objects.get(id=id)
            
            # Update fields
            product.name = input.name
            if input.get('sku'):
                product.sku = input.sku
            if input.get('slug'):
                product.slug = input.slug
            
            # Update brand if provided
            if input.brand_id:
                product.brand = Brand.objects.get(id=input.brand_id)
            
            # Update category if provided
            if input.category_id:
                product.category = Category.objects.get(id=input.category_id)
            
            # Update optional fields
            if input.get('description') is not None:
                product.description = input.description
            if input.get('short_description') is not None:
                product.short_description = input.short_description
            if input.get('ingredients') is not None:
                product.ingredients = input.ingredients
            if input.get('allergen_info') is not None:
                product.allergen_info = input.allergen_info
            if input.get('weight') is not None:
                product.weight = input.weight
            if input.get('volume') is not None:
                product.volume = input.volume
            if input.get('unit_type') is not None:
                product.unit_type = input.unit_type
            if input.get('is_active') is not None:
                product.is_active = input.is_active
            if input.get('featured') is not None:
                product.featured = input.featured
            
            product.save()
            
            return UpdateProduct(
                product=product,
                success=True,
                message=f"Product '{product.name}' updated successfully"
            )
        except Product.DoesNotExist:
            return UpdateProduct(success=False, message="Product not found")
        except (Brand.DoesNotExist, Category.DoesNotExist):
            return UpdateProduct(success=False, message="Brand or Category not found")
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'sku' in error_str:
                return UpdateProduct(success=False, message="A product with this SKU already exists")
            elif 'slug' in error_str:
                return UpdateProduct(success=False, message="A product with this slug already exists")
            logger.error(f"Integrity error updating product: {str(e)}")
            return UpdateProduct(success=False, message="Failed to update product due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error updating product: {str(e)}")
            return UpdateProduct(success=False, message=f"Invalid product data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}", exc_info=True)
            return UpdateProduct(success=False, message="Failed to update product. Please try again.")


class DeleteProduct(graphene.Mutation):
    """Delete a product (or mark as inactive)"""
    class Arguments:
        id = graphene.Int(required=True)
        hard_delete = graphene.Boolean()  # True = delete, False = deactivate
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, hard_delete=False):
        _require_staff(info)
        try:
            product = Product.objects.get(id=id)
            product_name = product.name
            
            if hard_delete:
                product.delete()
                message = f"Product '{product_name}' deleted permanently"
            else:
                product.is_active = False
                product.save()
                message = f"Product '{product_name}' deactivated"
            
            return DeleteProduct(success=True, message=message)
        except Product.DoesNotExist:
            return DeleteProduct(success=False, message="Product not found")
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}", exc_info=True)
            return DeleteProduct(success=False, message="Failed to delete product. Please try again.")


class SetProductPrice(graphene.Mutation):
    """Set or update product price"""
    class Arguments:
        input = ProductPriceInput(required=True)
    
    price = graphene.Field(ProductPriceType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            product = Product.objects.get(id=input.product_id)
            
            # Get or create price
            price, created = ProductPrice.objects.get_or_create(
                product=product,
                price_type=input.price_type,
                min_quantity=input.get('min_quantity', 1),
                defaults={
                    'base_price': input.base_price,
                    'sale_price': input.get('sale_price'),
                    'is_active': input.get('is_active', True)
                }
            )
            
            if not created:
                # Update existing price
                price.base_price = input.base_price
                if input.get('sale_price') is not None:
                    price.sale_price = input.sale_price
                if input.get('is_active') is not None:
                    price.is_active = input.is_active
                price.save()
            
            action = "created" if created else "updated"
            return SetProductPrice(
                price=price,
                success=True,
                message=f"Price {action} for '{product.name}'"
            )
        except Product.DoesNotExist:
            return SetProductPrice(success=False, message="Product not found")
        except IntegrityError as e:
            logger.error(f"Integrity error setting product price: {str(e)}")
            return SetProductPrice(success=False, message="Failed to set price due to a constraint violation")
        except ValidationError as e:
            logger.error(f"Validation error setting product price: {str(e)}")
            return SetProductPrice(success=False, message=f"Invalid price data: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            logger.error(f"Error setting product price: {str(e)}", exc_info=True)
            return SetProductPrice(success=False, message="Failed to set product price. Please try again.")


class UpdateInventory(graphene.Mutation):
    """Update product inventory"""
    class Arguments:
        input = InventoryInput(required=True)
    
    inventory = graphene.Field(InventoryType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            product = Product.objects.get(id=input.product_id)
            
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                defaults={
                    'quantity_in_stock': input.quantity_in_stock,
                    'low_stock_threshold': input.get('low_stock_threshold', 10),
                    'warehouse_location': input.get('warehouse_location', '')
                }
            )
            
            if not created:
                inventory.quantity_in_stock = input.quantity_in_stock
                if input.get('low_stock_threshold') is not None:
                    inventory.low_stock_threshold = input.low_stock_threshold
                if input.get('warehouse_location') is not None:
                    inventory.warehouse_location = input.warehouse_location
                inventory.save()
            
            return UpdateInventory(
                inventory=inventory,
                success=True,
                message=f"Inventory updated for '{product.name}': {inventory.quantity_in_stock} units"
            )
        except Product.DoesNotExist:
            return UpdateInventory(success=False, message="Product not found")
        except ValueError as e:
            logger.error(f"Value error updating inventory: {str(e)}")
            return UpdateInventory(success=False, message="Invalid inventory quantity specified")
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}", exc_info=True)
            return UpdateInventory(success=False, message="Failed to update inventory. Please try again.")


class UploadProductImage(graphene.Mutation):
    """Upload product image with automatic resizing"""
    class Arguments:
        input = ProductImageInput(required=True)
    
    product_image = graphene.Field(ProductImageType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            # Get the product
            product = Product.objects.get(id=input.product_id)
            
            # Decode base64 image
            import base64
            image_data = input.image
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Create PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                pil_image = pil_image.convert('RGB')
            
            # Resize image (max 1200x1200, maintain aspect ratio)
            max_size = (1200, 1200)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Create thumbnail (300x300)
            thumbnail = pil_image.copy()
            thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Generate filename
            import uuid
            filename = f"{product.slug}_{uuid.uuid4().hex[:8]}.jpg"
            
            # Save main image
            main_image_io = io.BytesIO()
            pil_image.save(main_image_io, format='JPEG', quality=85, optimize=True)
            main_image_io.seek(0)
            
            # Save thumbnail
            thumbnail_io = io.BytesIO()
            thumbnail.save(thumbnail_io, format='JPEG', quality=80, optimize=True)
            thumbnail_io.seek(0)
            
            # Create ProductImage instance
            product_image = ProductImage(
                product=product,
                alt_text=input.get('alt_text', f"{product.name} image"),
                is_primary=input.get('is_primary', False),
                display_order=input.get('display_order', 0)
            )
            
            # Save the main image
            product_image.image.save(
                filename,
                ContentFile(main_image_io.getvalue()),
                save=False
            )
            
            # If this is the first image or marked as primary, make it primary
            if input.get('is_primary', False) or not product.images.exists():
                # Remove primary flag from other images
                ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
                product_image.is_primary = True
            
            product_image.save()
            
            return UploadProductImage(
                product_image=product_image,
                success=True,
                message=f"Image uploaded successfully for '{product.name}'"
            )
            
        except Product.DoesNotExist:
            return UploadProductImage(success=False, message="Product not found")
        except ValueError as e:
            logger.error(f"Value error uploading image: {str(e)}")
            return UploadProductImage(success=False, message="Invalid image data provided")
        except Exception as e:
            logger.error(f"Error uploading product image: {str(e)}", exc_info=True)
            return UploadProductImage(success=False, message="Failed to upload image. Please check the image format and try again.")


class DeleteProductImage(graphene.Mutation):
    """Delete a product image"""
    class Arguments:
        image_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, image_id):
        _require_staff(info)
        try:
            product_image = ProductImage.objects.get(id=image_id)
            product_name = product_image.product.name
            
            # Delete the image file
            if product_image.image:
                product_image.image.delete(save=False)
            
            # Delete the database record
            product_image.delete()
            
            return DeleteProductImage(
                success=True,
                message=f"Image deleted from '{product_name}'"
            )
            
        except ProductImage.DoesNotExist:
            return DeleteProductImage(success=False, message="Image not found")
        except Exception as e:
            logger.error(f"Error deleting product image: {str(e)}", exc_info=True)
            return DeleteProductImage(success=False, message="Failed to delete image. Please try again.")


class SetPrimaryImage(graphene.Mutation):
    """Set a product image as primary"""
    class Arguments:
        image_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, image_id):
        _require_staff(info)
        try:
            product_image = ProductImage.objects.get(id=image_id)
            product = product_image.product
            
            # Remove primary flag from other images of this product
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
            
            # Set this image as primary
            product_image.is_primary = True
            product_image.save()
            
            return SetPrimaryImage(
                success=True,
                message=f"Primary image set for '{product.name}'"
            )
            
        except ProductImage.DoesNotExist:
            return SetPrimaryImage(success=False, message="Image not found")
        except Exception as e:
            logger.error(f"Error setting primary image: {str(e)}", exc_info=True)
            return SetPrimaryImage(success=False, message="Failed to set primary image. Please try again.")


# ============================================================================
# Product Variant Input Types
# ============================================================================

class VariantOptionInput(graphene.InputObjectType):
    """Input for creating variant options"""
    name = graphene.String(required=True, description="Option name (e.g., Color, Weight, Size)")
    values = graphene.List(graphene.String, required=True, description="List of option values")
    display_order = graphene.Int(description="Display order")


class ProductVariantInput(graphene.InputObjectType):
    """Input for creating/updating product variants"""
    product_id = graphene.Int(required=True)
    sku = graphene.String(required=True)
    option_values = graphene.JSONString(required=True, description="JSON object with option names and values")
    price = graphene.Decimal(required=True)
    sale_price = graphene.Decimal()
    currency = graphene.String()
    quantity_in_stock = graphene.Int()
    low_stock_threshold = graphene.Int()
    weight = graphene.Decimal()
    is_active = graphene.Boolean()
    is_default = graphene.Boolean()


# ============================================================================
# Product Variant Mutations
# ============================================================================

class CreateVariantOptions(graphene.Mutation):
    """Create variant options for a product (e.g., Color: White/Dark, Weight: 500g/1000g)"""
    class Arguments:
        product_id = graphene.Int(required=True)
        options = graphene.List(VariantOptionInput, required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    variant_options = graphene.List(ProductVariantOptionType)
    
    def mutate(self, info, product_id, options):
        _require_staff(info)
        try:
            product = Product.objects.get(id=product_id)
            created_options = []
            
            for option_input in options:
                # Create the option
                option = ProductVariantOption.objects.create(
                    product=product,
                    name=option_input.name,
                    display_order=option_input.get('display_order', 0)
                )
                
                # Create option values
                for idx, value in enumerate(option_input.values):
                    ProductVariantOptionValue.objects.create(
                        option=option,
                        value=value,
                        display_order=idx
                    )
                
                created_options.append(option)
            
            return CreateVariantOptions(
                success=True,
                message=f"Created {len(created_options)} variant options for '{product.name}'",
                variant_options=created_options
            )
            
        except Product.DoesNotExist:
            return CreateVariantOptions(success=False, message="Product not found")
        except IntegrityError as e:
            logger.error(f"Integrity error creating variant options: {str(e)}")
            return CreateVariantOptions(success=False, message="Failed to create variant options due to a constraint violation")
        except Exception as e:
            logger.error(f"Error creating variant options: {str(e)}", exc_info=True)
            return CreateVariantOptions(success=False, message="Failed to create variant options. Please try again.")


class CreateProductVariant(graphene.Mutation):
    """Create a product variant (e.g., Coco Mass White 500g)"""
    class Arguments:
        input = ProductVariantInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    variant = graphene.Field(ProductVariantType)
    
    def mutate(self, info, input):
        _require_staff(info)
        try:
            from django.db import transaction
            import json
            
            product = Product.objects.get(id=input.product_id)
            
            # Check if SKU already exists
            if ProductVariant.objects.filter(sku=input.sku).exists():
                return CreateProductVariant(success=False, message=f"SKU '{input.sku}' already exists")
            
            with transaction.atomic():
                # Create the variant
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=input.sku,
                    price=input.price,
                    sale_price=input.get('sale_price'),
                    currency=input.get('currency', 'AED'),
                    quantity_in_stock=input.get('quantity_in_stock', 0),
                    reserved_quantity=0,
                    low_stock_threshold=input.get('low_stock_threshold', 10),
                    weight=input.get('weight'),
                    is_active=input.get('is_active', True),
                    is_default=input.get('is_default', False)
                )
                
                # Parse option values from JSON
                # Expected format: {"Color": "White", "Weight": "500g"}
                option_values_dict = json.loads(input.option_values) if isinstance(input.option_values, str) else input.option_values
                
                # Link variant to option values
                for option_name, option_value in option_values_dict.items():
                    try:
                        option = ProductVariantOption.objects.get(product=product, name=option_name)
                        value = ProductVariantOptionValue.objects.get(option=option, value=option_value)
                        
                        ProductVariantValue.objects.create(
                            variant=variant,
                            option_value=value
                        )
                    except (ProductVariantOption.DoesNotExist, ProductVariantOptionValue.DoesNotExist):
                        raise Exception(f"Option '{option_name}' with value '{option_value}' not found")
                
                # If this is the default variant, unset others
                if input.get('is_default', False):
                    ProductVariant.objects.filter(product=product).exclude(id=variant.id).update(is_default=False)
                
                return CreateProductVariant(
                    success=True,
                    message=f"Variant '{variant.sku}' created successfully",
                    variant=variant
                )
        
        except Product.DoesNotExist:
            return CreateProductVariant(success=False, message="Product not found")
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'sku' in error_str:
                return CreateProductVariant(success=False, message="A variant with this SKU already exists")
            logger.error(f"Integrity error creating product variant: {str(e)}")
            return CreateProductVariant(success=False, message="Failed to create variant due to a constraint violation")
        except ValueError as e:
            logger.error(f"Value error creating variant: {str(e)}")
            return CreateProductVariant(success=False, message="Invalid variant data provided")
        except Exception as e:
            logger.error(f"Error creating product variant: {str(e)}", exc_info=True)
            return CreateProductVariant(success=False, message="Failed to create variant. Please try again.")


class UpdateProductVariant(graphene.Mutation):
    """Update a product variant"""
    class Arguments:
        variant_id = graphene.Int(required=True)
        price = graphene.Decimal()
        sale_price = graphene.Decimal()
        quantity_in_stock = graphene.Int()
        low_stock_threshold = graphene.Int()
        is_active = graphene.Boolean()
        is_default = graphene.Boolean()
    
    success = graphene.Boolean()
    message = graphene.String()
    variant = graphene.Field(ProductVariantType)
    
    def mutate(self, info, variant_id, **kwargs):
        _require_staff(info)
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            
            # Update fields
            if 'price' in kwargs and kwargs['price'] is not None:
                variant.price = kwargs['price']
            if 'sale_price' in kwargs:
                variant.sale_price = kwargs['sale_price']
            if 'quantity_in_stock' in kwargs and kwargs['quantity_in_stock'] is not None:
                variant.quantity_in_stock = kwargs['quantity_in_stock']
            if 'low_stock_threshold' in kwargs and kwargs['low_stock_threshold'] is not None:
                variant.low_stock_threshold = kwargs['low_stock_threshold']
            if 'is_active' in kwargs and kwargs['is_active'] is not None:
                variant.is_active = kwargs['is_active']
            if 'is_default' in kwargs and kwargs['is_default'] is not None:
                variant.is_default = kwargs['is_default']
                # If setting as default, unset others
                if kwargs['is_default']:
                    ProductVariant.objects.filter(product=variant.product).exclude(id=variant.id).update(is_default=False)
            
            variant.save()
            
            return UpdateProductVariant(
                success=True,
                message=f"Variant '{variant.sku}' updated successfully",
                variant=variant
            )
        
        except ProductVariant.DoesNotExist:
            return UpdateProductVariant(success=False, message="Variant not found")
        except ValueError as e:
            logger.error(f"Value error updating variant: {str(e)}")
            return UpdateProductVariant(success=False, message="Invalid variant data provided")
        except Exception as e:
            logger.error(f"Error updating product variant: {str(e)}", exc_info=True)
            return UpdateProductVariant(success=False, message="Failed to update variant. Please try again.")


class DeleteProductVariant(graphene.Mutation):
    """Delete a product variant"""
    class Arguments:
        variant_id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, variant_id):
        _require_staff(info)
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            sku = variant.sku
            variant.delete()
            
            return DeleteProductVariant(
                success=True,
                message=f"Variant '{sku}' deleted successfully"
            )
        
        except ProductVariant.DoesNotExist:
            return DeleteProductVariant(success=False, message="Variant not found")
        except Exception as e:
            logger.error(f"Error deleting product variant: {str(e)}", exc_info=True)
            return DeleteProductVariant(success=False, message="Failed to delete variant. Please try again.")


# Mutation class for Products Admin
class ProductAdminMutation(graphene.ObjectType):
    """All product admin mutations"""
    # Categories
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    
    # Brands
    create_brand = CreateBrand.Field()
    update_brand = UpdateBrand.Field()
    
    # Products
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    
    # Pricing
    set_product_price = SetProductPrice.Field()
    
    # Inventory
    update_inventory = UpdateInventory.Field()
    
    # Images
    upload_product_image = UploadProductImage.Field()
    delete_product_image = DeleteProductImage.Field()
    set_primary_image = SetPrimaryImage.Field()
    
    # Variants
    create_variant_options = CreateVariantOptions.Field()
    create_product_variant = CreateProductVariant.Field()
    update_product_variant = UpdateProductVariant.Field()
    delete_product_variant = DeleteProductVariant.Field()


# Main Mutation class - exports all product mutations
class ProductMutation(ProductAdminMutation, graphene.ObjectType):
    """All product mutations for GraphQL schema"""
    pass

