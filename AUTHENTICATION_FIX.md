# Authentication Fix - Header Format Issue

## Problem
Frontend was getting "Not authorized" errors when trying to create categories and perform admin operations.

## Root Cause
The backend is configured to expect `Bearer` prefix in the Authorization header, but the frontend was likely sending `JWT` prefix (or the documentation showed the wrong format).

## Solution

### Backend Configuration
The backend expects:
```
Authorization: Bearer <jwt-token>
```

Configured in `ecomarce_choco/settings.py`:
```python
GRAPHQL_JWT = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}
```

### Frontend Fix Required
Update your frontend to send the Authorization header with `Bearer` prefix:

```javascript
// ✅ CORRECT
headers: {
  'Authorization': `Bearer ${token}`
}

// ❌ WRONG (will cause "Not authorized" error)
headers: {
  'Authorization': `JWT ${token}`
}
```

## Changes Made

1. **Improved Error Messages** (`products/schema.py` and `orders/schema.py`):
   - More descriptive error messages that distinguish between:
     - Unauthenticated (no token or invalid token)
     - Authenticated but not staff (token valid but user lacks permissions)

2. **Updated Documentation**:
   - `FRONTEND_INTEGRATION.md` - Fixed header format to show `Bearer`
   - `ADMIN_GUIDE.md` - Fixed header format and added troubleshooting section

3. **Better Logging**:
   - Errors now log the Authorization header received (without exposing full token)
   - Logs which user attempted the operation and their staff status

## How to Verify

1. **Check if token is being recognized:**
   ```graphql
   query {
     me {
       id
       username
       isStaff
     }
   }
   ```
   If this returns `null`, the token is not being recognized → Check header format.

2. **Check if user is staff:**
   If `me` query works but admin mutations fail:
   - Verify `isStaff` is `true` in the `me` query response
   - User must have staff privileges in Django admin

## Additional Checks

1. **Token Expiration**: JWT tokens expire after 7 days
2. **User Must Be Staff**: Even with valid token, user needs `is_staff = True`
3. **CORS**: Frontend domain must be in `CORS_ALLOWED_ORIGINS`

## Quick Test

Test the authentication with this mutation (should work with correct header):

```graphql
mutation {
  createCategory(input: {
    name: "Test Category"
    slug: "test-category"
    isActive: true
  }) {
    success
    message
    category {
      id
      name
    }
  }
}
```

If you still get "Not authorized":
1. Verify header is `Authorization: Bearer <token>` (not `JWT`)
2. Run `me` query to verify token is recognized
3. Check if `isStaff` is `true` in the `me` response

