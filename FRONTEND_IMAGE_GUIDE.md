# 🖼️ Frontend Guide: Product Images

Complete guide for frontend developers on how to work with product images.

---

## 📋 Overview

Products can have multiple images:
- **Main Images** (up to 3 per product) - Primary product photos
- **Use Case Images** (up to 4 per product) - Additional product images

Each product has:
- A **primary image** (marked with `isPrimary: true`)
- Multiple **additional images** for galleries
- **Alt text** for accessibility

---

## 📁 Where Images Are Stored

### **On the Server (Backend)**

Images are stored on the backend server in the `media/` directory:

**Server File Path:**
```
/home/django/ecomarce_choco/media/
```

**Directory Structure:**
```
media/
├── products/              # Main product images
│   ├── product-name_abc123.jpg
│   └── product-name_def456.jpg
├── products/usecase/      # Use case images
│   ├── usecase-name_ghi789.jpg
│   └── usecase-name_jkl012.jpg
├── categories/            # Category images
│   └── category-name_mno345.jpg
├── brands/                # Brand logos
│   └── brand-name_pqr678.jpg
└── variants/              # Variant-specific images
    └── variant-name_stu901.jpg
```

### **Image Storage Locations by Type**

| Image Type | Server Path | URL Path | Example |
|------------|-------------|----------|---------|
| **Product Images** | `media/products/` | `/media/products/` | `/media/products/lindt-chocolate_a1b2c3d4.jpg` |
| **Use Case Images** | `media/products/usecase/` | `/media/products/usecase/` | `/media/products/usecase/gift-box_e5f6g7h8.jpg` |
| **Category Images** | `media/categories/` | `/media/categories/` | `/media/categories/premium-chocolates_i3j4k5l6.jpg` |
| **Brand Logos** | `media/brands/` | `/media/brands/` | `/media/brands/lindt-logo_m7n8o9p0.jpg` |
| **Variant Images** | `media/variants/` | `/media/variants/` | `/media/variants/variant-500g_n1o2p3q4.jpg` |

### **How Images Are Accessed**

1. **Upload:** Images are uploaded via GraphQL mutation (base64 encoded)
2. **Storage:** Backend saves them to the `media/` directory on the server
3. **URL:** Images are served at `/media/` URL path
4. **Access:** Frontend accesses images via full URL: `https://164.90.215.173/media/...`

---

## 🔗 Image URLs

### **How Images Are Returned**

When you query products, images come as **relative paths**:

```graphql
query {
  product(id: 1) {
    name
    images {
      id
      image        # Returns: "/media/products/lindt-dark-chocolate_a1b2c3d4.jpg"
      altText
      isPrimary
      displayOrder
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "product": {
      "name": "Lindt Dark Chocolate",
      "images": [
        {
          "id": "1",
          "image": "/media/products/lindt-dark-chocolate_a1b2c3d4.jpg",
          "altText": "Lindt Dark Chocolate Bar",
          "isPrimary": true,
          "displayOrder": 1
        },
        {
          "id": "2",
          "image": "/media/products/lindt-dark-chocolate_e5f6g7h8.jpg",
          "altText": "Lindt Dark Chocolate - Side View",
          "isPrimary": false,
          "displayOrder": 2
        }
      ]
    }
  }
}
```

### **Building Full Image URLs**

You need to prepend the backend URL to get the full image URL:

**Backend URL:** `https://164.90.215.173`

**Image path from GraphQL:** `/media/products/lindt-dark-chocolate_a1b2c3d4.jpg`

**Full URL for `<img>` tag:**
```
https://164.90.215.173/media/products/lindt-dark-chocolate_a1b2c3d4.jpg
```

**Formula:**
```
Full Image URL = Backend URL + Image Path
```

---

## 📝 GraphQL Queries

### **Get Product with Images**

```graphql
query GetProduct($id: ID!) {
  product(id: $id) {
    id
    name
    slug
    description
    images {
      id
      image
      altText
      isPrimary
      displayOrder
    }
    usecaseImages {
      id
      image
      altText
      displayOrder
    }
    retailPrice
  }
}
```

### **Get Products List with Images**

```graphql
query GetProducts($limit: Int) {
  products(limit: $limit) {
    id
    name
    slug
    images {
      id
      image
      altText
      isPrimary
      displayOrder
    }
    retailPrice
    inStock
  }
}
```

### **Get Featured Products with Images**

```graphql
query GetFeaturedProducts {
  products(featured: true, limit: 10) {
    id
    name
    images {
      id
      image
      altText
      isPrimary
    }
    retailPrice
  }
}
```

---

## 🖼️ Image Data Structure

### **ProductImage Fields**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Unique image ID |
| `image` | String | Relative path to image (e.g., `/media/products/filename.jpg`) |
| `altText` | String | Alt text for accessibility |
| `isPrimary` | Boolean | `true` if this is the primary/main image |
| `displayOrder` | Int | Order for displaying images (1, 2, 3...) |

### **ProductImageUseCase Fields**

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Unique image ID |
| `image` | String | Relative path to image |
| `altText` | String | Alt text for accessibility |
| `displayOrder` | Int | Order for displaying images |

---

## 🔍 Finding the Primary Image

### **Method 1: Find Image with `isPrimary: true`**

Look for the image where `isPrimary` is `true`. This is the main product image.

### **Method 2: Fallback to First Image**

If no image has `isPrimary: true`, use the first image in the array.

### **Method 3: Sort by Display Order**

Sort images by `displayOrder` field (ascending), then use the first one.

---

## 📊 Image URL Examples

### **Example 1: Product Image**

**GraphQL Response:**
```json
{
  "image": "/media/products/lindt-dark-chocolate_a1b2c3d4.jpg"
}
```

**Full URL:**
```
https://164.90.215.173/media/products/lindt-dark-chocolate_a1b2c3d4.jpg
```

### **Example 2: Use Case Image**

**GraphQL Response:**
```json
{
  "image": "/media/products/usecase/chocolate-gift-box_e9f0g1h2.jpg"
}
```

**Full URL:**
```
https://164.90.215.173/media/products/usecase/chocolate-gift-box_e9f0g1h2.jpg
```

### **Example 3: Category Image**

**GraphQL Response:**
```json
{
  "image": "/media/categories/premium-chocolates_i3j4k5l6.jpg"
}
```

**Full URL:**
```
https://164.90.215.173/media/categories/premium-chocolates_i3j4k5l6.jpg
```

### **Example 4: Brand Logo**

**GraphQL Response:**
```json
{
  "logo": "/media/brands/lindt-logo_m7n8o9p0.jpg"
}
```

**Full URL:**
```
https://164.90.215.173/media/brands/lindt-logo_m7n8o9p0.jpg
```

---

## ⚠️ Important Notes

### **1. Always Use HTTPS**

Since your frontend is on HTTPS (`https://clownfish-app-2ehbt.ondigitalocean.app`), all image URLs must also use HTTPS:

**✅ Correct:**
```
https://164.90.215.173/media/products/image.jpg
```

**❌ Wrong - Will cause mixed content error:**
```
http://164.90.215.173/media/products/image.jpg
```

### **2. Handle Missing Images**

Always check if image exists before displaying:
- If `image` field is `null` or empty, show a placeholder
- If image fails to load, show a fallback image

### **3. Use Alt Text for Accessibility**

Always use the `altText` from the API or fallback to product name:
- Use `altText` field from the image object
- If `altText` is empty, use the product name

### **4. Image Ordering**

Images are returned in `displayOrder` order, but you should:
- Sort by `displayOrder` (ascending: 1, 2, 3...)
- Display primary image first (where `isPrimary: true`)
- Show additional images in a gallery

### **5. Image Sizes**

Images are automatically optimized by the backend:
- Main images: Max 1200x1200 pixels
- Thumbnails: 300x300 pixels
- Format: JPEG, 85% quality

---

## 🎨 Display Recommendations

### **Product Card (List View)**
- Show **primary image** or **first image**
- Use thumbnail size (300x300)
- Lazy load images for better performance

### **Product Detail Page**
- Show **primary image** as main image (large)
- Show all images in a **thumbnail gallery**
- Allow users to click thumbnails to change main image
- Display images in `displayOrder` sequence

### **Image Gallery**
- Display all product images
- Show primary image first
- Sort by `displayOrder`
- Include use case images if available

---

## 🧪 Testing Image URLs

### **Test 1: Direct Browser Access**

Open in browser:
```
https://164.90.215.173/media/products/godiva-truffle-assortment_cda8730f.jpg
```

**Expected:** Image displays
**If blocked:** Accept the SSL certificate first (self-signed certificate warning)

### **Test 2: GraphQL Query**

Run this query:
```graphql
query {
  product(id: 1) {
    name
    images {
      image
      altText
      isPrimary
    }
  }
}
```

**Check:**
- Image paths start with `/media/`
- Paths are valid file paths
- Primary image is marked correctly

### **Test 3: Verify Full URL**

Construct full URL and test:
1. Get image path from GraphQL: `/media/products/filename.jpg`
2. Prepend backend URL: `https://164.90.215.173`
3. Result: `https://164.90.215.173/media/products/filename.jpg`
4. Open in browser to verify it loads

---

## 📋 Image Path Patterns

### **Product Images**
```
/media/products/{product-slug}_{random-id}.jpg
```

**Example:**
```
/media/products/lindt-dark-chocolate_a1b2c3d4.jpg
```

### **Use Case Images**
```
/media/products/usecase/{product-slug}_{random-id}.jpg
```

**Example:**
```
/media/products/usecase/chocolate-gift-box_e5f6g7h8.jpg
```

### **Category Images**
```
/media/categories/{category-slug}_{random-id}.jpg
```

**Example:**
```
/media/categories/premium-chocolates_i3j4k5l6.jpg
```

### **Brand Logos**
```
/media/brands/{brand-slug}_{random-id}.jpg
```

**Example:**
```
/media/brands/lindt-logo_m7n8o9p0.jpg
```

---

## 🔄 Complete Product Query Example

```graphql
query GetCompleteProduct($id: ID!) {
  product(id: $id) {
    id
    name
    slug
    description
    sku
    
    # Main product images (up to 3)
    images {
      id
      image              # Relative path: "/media/products/..."
      altText
      isPrimary
      displayOrder
    }
    
    # Use case images (up to 4)
    usecaseImages {
      id
      image              # Relative path: "/media/products/usecase/..."
      altText
      displayOrder
    }
    
    # Category image
    category {
      id
      name
      image             # Relative path: "/media/categories/..."
    }
    
    # Brand logo
    brand {
      id
      name
      logo             # Relative path: "/media/brands/..."
    }
    
    # Pricing
    retailPrice
    
    # Stock status
    inStock
  }
}
```

---

## ✅ Implementation Checklist

Before implementing, make sure:

- [ ] Backend URL is set: `https://164.90.215.173`
- [ ] All image URLs use `https://` (not `http://`)
- [ ] Image URLs are constructed correctly: `Backend URL + Image Path`
- [ ] Missing images are handled gracefully (show placeholder)
- [ ] Alt text is used for all images (from API or product name)
- [ ] Primary image is selected correctly (`isPrimary: true` or first image)
- [ ] Images are sorted by `displayOrder`
- [ ] Error handling is implemented for failed image loads
- [ ] Images are lazy loaded in product lists (for performance)

---

## 🚀 Quick Reference

### **Backend URL**
```
https://164.90.215.173
```

### **Image URL Formula**
```
Full Image URL = https://164.90.215.173 + Image Path
```

### **Example**
```
Image Path: /media/products/lindt-dark-chocolate_a1b2c3d4.jpg
Full URL: https://164.90.215.173/media/products/lindt-dark-chocolate_a1b2c3d4.jpg
```

### **Primary Image Selection**
1. Find image where `isPrimary: true`
2. If not found, use first image in array
3. Sort by `displayOrder` if needed

---

## 📞 Support

### **Common Issues**

**Issue:** Images not loading
- Check URL uses `https://` (not `http://`)
- Verify image path is correct
- Test direct URL in browser

**Issue:** Mixed content error
- Ensure all URLs use `https://`
- Check browser console for errors

**Issue:** Certificate warning
- Accept certificate in browser (temporary)
- For production: Use Let's Encrypt with domain

**Issue:** Missing images
- Check if `image` field is null
- Show placeholder image
- Handle image load errors

---

**That's it!** You now know how to work with product images. 🎉
