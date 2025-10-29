# 📸 Image Upload Guide

Complete guide for uploading product images to your chocolate store.

---

## 🎯 **What's Implemented**

### **✅ Image Upload Features:**
- ✅ **Base64 image upload** via GraphQL
- ✅ **Automatic image resizing** (max 1200x1200)
- ✅ **Thumbnail generation** (300x300)
- ✅ **Image optimization** (JPEG, quality 85%)
- ✅ **Multiple images per product**
- ✅ **Primary image selection**
- ✅ **Image deletion**
- ✅ **Alt text support**

---

## 🚀 **How to Upload Images**

### **1. Upload Product Image**

```graphql
mutation {
  uploadProductImage(input: {
    productId: 1
    image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
    altText: "Lindt Dark Chocolate Bar"
    isPrimary: true
    displayOrder: 1
  }) {
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
```

### **2. Set Primary Image**

```graphql
mutation {
  setPrimaryImage(imageId: 1) {
    success
    message
  }
}
```

### **3. Delete Product Image**

```graphql
mutation {
  deleteProductImage(imageId: 1) {
    success
    message
  }
}
```

---

## 📋 **Image Upload Process**

### **Step 1: Prepare Your Image**
1. **Take/select a product photo**
2. **Convert to base64** (see examples below)
3. **Ensure good quality** (high resolution recommended)

### **Step 2: Upload via GraphQL**
1. **Get product ID** from your products
2. **Encode image as base64**
3. **Use uploadProductImage mutation**
4. **Check success response**

### **Step 3: Manage Images**
1. **Set primary image** for product listing
2. **Reorder images** with displayOrder
3. **Delete unwanted images**

---

## 🛠️ **Technical Details**

### **Image Processing:**
- **Input**: Base64 encoded image (any format)
- **Processing**: Convert to RGB, resize, optimize
- **Output**: JPEG format, 85% quality
- **Sizes**: Main image (max 1200x1200), Thumbnail (300x300)
- **Storage**: `media/products/` directory

### **File Naming:**
- **Format**: `{product-slug}_{random-id}.jpg`
- **Example**: `lindt-dark-chocolate_a1b2c3d4.jpg`

### **Database Fields:**
- **product**: Link to product
- **image**: File path
- **alt_text**: Accessibility text
- **is_primary**: Main product image
- **display_order**: Sort order
- **created_at**: Upload timestamp

---

## 📝 **Examples**

### **JavaScript Frontend Example:**

```javascript
// Convert file to base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
}

// Upload image
async function uploadProductImage(productId, imageFile) {
  const base64Image = await fileToBase64(imageFile);
  
  const mutation = `
    mutation UploadImage($input: ProductImageInput!) {
      uploadProductImage(input: $input) {
        success
        message
        productImage {
          id
          image
          altText
          isPrimary
        }
      }
    }
  `;
  
  const variables = {
    input: {
      productId: productId,
      image: base64Image,
      altText: "Product image",
      isPrimary: true
    }
  };
  
  // Send to GraphQL endpoint
  const response = await fetch('/graphql/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: mutation, variables })
  });
  
  return response.json();
}
```

### **Python Example:**

```python
import base64
import requests

def upload_product_image(product_id, image_path):
    # Read and encode image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # GraphQL mutation
    mutation = """
    mutation UploadImage($input: ProductImageInput!) {
      uploadProductImage(input: $input) {
        success
        message
        productImage {
          id
          image
          altText
          isPrimary
        }
      }
    }
    """
    
    variables = {
        "input": {
            "productId": product_id,
            "image": f"data:image/jpeg;base64,{image_data}",
            "altText": "Product image",
            "isPrimary": True
        }
    }
    
    response = requests.post(
        'http://localhost:8000/graphql/',
        json={'query': mutation, 'variables': variables}
    )
    
    return response.json()
```

---

## 🎨 **Image Best Practices**

### **Recommended Specifications:**
- **Format**: JPEG or PNG
- **Size**: 1200x1200 pixels (square) or 1200x800 (landscape)
- **Quality**: High resolution for best results
- **Background**: White or transparent
- **Lighting**: Good, even lighting
- **Angle**: Straight-on product view

### **For Chocolate Products:**
- **Show texture** and details
- **Good lighting** to show color
- **Clean background**
- **Multiple angles** (front, back, side)
- **Packaging visible** if important

---

## 🔧 **Admin Interface**

### **Django Admin:**
- **View all images** in ProductImage section
- **Edit alt text** and display order
- **Set primary image** via admin
- **Delete images** directly

### **GraphQL Queries:**
```graphql
# Get product with images
query {
  product(id: 1) {
    id
    name
    images {
      id
      image
      altText
      isPrimary
      displayOrder
    }
  }
}
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

**1. Base64 Format Error:**
```
Error: Invalid base64 data
Solution: Ensure image is properly base64 encoded
```

**2. Image Too Large:**
```
Error: Image processing failed
Solution: Resize image before upload (max 5MB recommended)
```

**3. Product Not Found:**
```
Error: Product not found
Solution: Check product ID exists
```

**4. Permission Error:**
```
Error: Permission denied
Solution: Check media directory permissions
```

### **Debug Steps:**
1. **Check image format** (JPEG, PNG supported)
2. **Verify base64 encoding** (should start with `data:image/`)
3. **Test with small image** first
4. **Check server logs** for detailed errors

---

## 📊 **Image Management Workflow**

### **For New Products:**
1. **Create product** first
2. **Upload primary image** (isPrimary: true)
3. **Upload additional images** (isPrimary: false)
4. **Set display order** for gallery
5. **Add alt text** for accessibility

### **For Existing Products:**
1. **View current images** via GraphQL
2. **Upload new images** as needed
3. **Set new primary** if desired
4. **Delete old images** if replacing
5. **Reorder images** for best display

---

## 🎉 **Success!**

Your image upload system is now ready! You can:

✅ **Upload product images** via GraphQL  
✅ **Automatic resizing** and optimization  
✅ **Multiple images** per product  
✅ **Primary image** selection  
✅ **Image management** (delete, reorder)  
✅ **Alt text** for accessibility  

**Next steps:**
1. **Test with real product images**
2. **Build frontend image upload UI**
3. **Add image gallery** to product pages
4. **Implement image optimization** for web

---

**Ready to upload your first product image?** 🍫📸
