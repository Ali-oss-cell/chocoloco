"""
Django management command to fix unit_type from 'GRAMS' to 'GRAM'
Run: python manage.py fix_unit_type
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = "Fix unit_type from 'GRAMS' (plural) to 'GRAM' (singular) for all products"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all products with 'GRAMS'
        products = Product.objects.filter(unit_type='GRAMS')
        count = products.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No products with unit_type="GRAMS" found. All products are correct!')
            )
            return
        
        self.stdout.write(f'Found {count} product(s) with unit_type="GRAMS"')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY RUN - No changes will be made\n')
            )
            for product in products:
                self.stdout.write(f'  - ID {product.id}: {product.name} (SKU: {product.sku})')
            self.stdout.write(
                self.style.WARNING(f'\nTo apply these changes, run without --dry-run flag')
            )
        else:
            # Update all products
            updated = products.update(unit_type='GRAM')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully updated {updated} product(s) from "GRAMS" to "GRAM"'
                )
            )
            
            # Show updated products
            self.stdout.write('\nUpdated products:')
            for product in Product.objects.filter(id__in=products.values_list('id', flat=True)):
                self.stdout.write(f'  - ID {product.id}: {product.name} (SKU: {product.sku})')
