#!/usr/bin/env python3
"""
Test script for image upload functionality
Run this to test the image upload system
"""

import requests
import base64
import json
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a simple colored image
    img = Image.new('RGB', (800, 600), color='red')
    
    # Add some text (simulate product image)
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)   
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "TEST CHOCOLATE", fill='white', font=font)
    draw.text((50, 100), "Product Image", fill='white', font=font)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{image_data}"

def test_image_upload():
    """Test the image upload mutation"""
    
    # First, let's check if we have any products
    check_products_query = """
    query {
      products {
        id
        name
        sku
      }
    }
    """
    
    print("🔍 Checking for existing products...")
    response = requests.post(
        'http://localhost:8000/graphql/',
        json={'query': check_products_query}
    )
    
    if response.status_code != 200:
        print("❌ Server not running! Start with: python manage.py runserver")
        return
    
    data = response.json()
    products = data.get('data', {}).get('products', [])
    
    if not products:
        print("❌ No products found! Create a product first.")
        print("💡 Use the admin interface or GraphQL mutations to create a product.")
        return
    
    print(f"✅ Found {len(products)} products")
    product = products[0]  # Use first product
    print(f"📦 Using product: {product['name']} (ID: {product['id']})")
    
    # Create test image
    print("🖼️ Creating test image...")
    test_image = create_test_image()
    
    # Upload image mutation
    upload_mutation = """
    mutation UploadImage($input: ProductImageInput!) {
      uploadProductImage(input: $input) {
        success
        message
        productImage {
          id
          altText
          isPrimary
          displayOrder
          image
        }
      }
    }
    """
    
    variables = {
        "input": {
            "productId": int(product['id']),  # Ensure it's an integer
            "image": test_image,
            "altText": f"Test image for {product['name']}",
            "isPrimary": True,
            "displayOrder": 1
        }
    }
    
    print("📤 Uploading image...")
    response = requests.post(
        'http://localhost:8000/graphql/',
        json={'query': upload_mutation, 'variables': variables}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('data', {}).get('uploadProductImage', {}).get('success'):
            print("✅ Image uploaded successfully!")
            print(f"📝 Message: {result['data']['uploadProductImage']['message']}")
            
            # Get the uploaded image info
            image_info = result['data']['uploadProductImage']['productImage']
            print(f"🆔 Image ID: {image_info['id']}")
            print(f"📷 Alt Text: {image_info['altText']}")
            print(f"⭐ Primary: {image_info['isPrimary']}")
            print(f"📁 Image URL: {image_info['image']}")
            
        else:
            print("❌ Upload failed!")
            print(f"Error: {result.get('data', {}).get('uploadProductImage', {}).get('message', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")

def test_get_product_images():
    """Test getting product images"""
    
    # First get a product
    products_query = """
    query {
      products {
        id
        name
        images {
          id
          altText
          isPrimary
          displayOrder
          image
        }
      }
    }
    """
    
    print("\n🔍 Getting product images...")
    response = requests.post(
        'http://localhost:8000/graphql/',
        json={'query': products_query}
    )
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('data', {}).get('products', [])
        
        for product in products:
            print(f"\n📦 Product: {product['name']}")
            images = product.get('images', [])
            if images:
                print(f"📷 Images ({len(images)}):")
                for img in images:
                    print(f"  - ID: {img['id']}, Primary: {img['isPrimary']}, Alt: {img['altText']}")
            else:
                print("📷 No images")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    print("🍫 Chocolate Store - Image Upload Test")
    print("=" * 50)
    
    try:
        test_image_upload()
        test_get_product_images()
        
        print("\n🎉 Test completed!")
        print("\n💡 Next steps:")
        print("1. Check the media/products/ directory for uploaded images")
        print("2. Test with real product images")
        print("3. Build frontend image upload UI")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure server is running: python manage.py runserver")
        print("2. Check that you have products in the database")
        print("3. Verify Pillow is installed: pip install Pillow")
