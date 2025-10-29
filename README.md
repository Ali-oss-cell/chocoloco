# 🍫 E-Commerce Chocolate Platform

A comprehensive e-commerce backend built with Django and GraphQL for a chocolate retail and wholesale business based in UAE.

## 🚀 Launch Strategy

**Phase 1 (NOW)**: Retail customers only - fast launch in 4-6 weeks  
**Phase 2 (FUTURE)**: Add wholesale when ready - easy to enable

📖 See [LAUNCH_STRATEGY.md](LAUNCH_STRATEGY.md) for complete strategy

## 📋 Documentation

**📖 [Complete Project Plan & Implementation Guide](PROJECT_PLAN.md)**

The `PROJECT_PLAN.md` file contains:
- Complete database models with code
- Phase-by-phase TODO list with checkboxes
- GraphQL API structure
- Payment gateway integration guides
- UAE-specific business requirements
- Quick start commands

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install graphene-django django-graphql-jwt django-cors-headers pillow django-filter python-decouple
pip freeze > requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the template and fill in your values
cp env_template.txt .env
# Edit .env with your actual credentials
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

### 7. Access Admin & GraphQL
- Admin: http://localhost:8000/admin
- GraphQL: http://localhost:8000/graphql (after setup)

## 🏗️ Project Structure

```
ecomarce_choco/
├── users/          # User management (Staff & Wholesale)
├── products/       # Products, Categories, Brands, Pricing
├── orders/         # Cart, Orders, Shipping
├── payments/       # Payment Gateways (Tabby, Tamara, Network)
└── ecomarce_choco/ # Main project settings
```

## 🎯 Key Features

### For Retail Customers (No Login Required)
- Browse products by category and brand
- Add to cart without account
- Checkout with guest details
- Multiple payment options (Tabby, Tamara, Network, COD)

### For Wholesale Customers (PHASE 2 - FUTURE)
- Special wholesale pricing
- Bulk order capabilities
- Credit limit management
- Order history and tracking
- Custom payment terms

**Note**: Wholesale features are ready but commented out. Enable when needed!

### For Admin
- Product management with pricing
- Inventory management with alerts
- Order processing and status updates
- Payment and refund management
- Sales reports and analytics
- (Phase 2: Wholesale account management)

## 💳 Payment Gateways

- **Tabby**: Buy Now Pay Later (BNPL)
- **Tamara**: Buy Now Pay Later (BNPL)
- **Network International**: Card payments with 3D Secure

## 🇦🇪 UAE-Specific Features

- VAT calculation (5%)
- Emirates-based delivery fees
- AED currency
- Trade license verification for wholesale
- Arabic language support (future)

## 📊 Tech Stack

- **Backend**: Django 5.1
- **API**: GraphQL (Graphene-Django)
- **Database**: SQLite (dev), PostgreSQL (production)
- **Authentication**: JWT for wholesale customers
- **Frontend**: React (separate repository)

## 📝 Next Steps

Follow the detailed implementation guide in **[PROJECT_PLAN.md](PROJECT_PLAN.md)** starting with Phase 1.

### Immediate Tasks
1. ✅ Review PROJECT_PLAN.md
2. ⬜ Install GraphQL dependencies
3. ⬜ Implement database models
4. ⬜ Set up admin interface
5. ⬜ Create GraphQL schema
6. ⬜ Integrate payment gateways

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep payment gateway credentials secure
- Use environment variables for all sensitive data
- Enable HTTPS in production
- Implement rate limiting on public APIs

## 📞 Support

For detailed implementation steps, business logic, and code examples, refer to:
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Complete implementation guide

## 📄 License

Proprietary - All rights reserved

---

**Location**: UAE  
**Focus**: Backend Development  
**Version**: 1.0  
**Last Updated**: October 12, 2025

# chocoloco
