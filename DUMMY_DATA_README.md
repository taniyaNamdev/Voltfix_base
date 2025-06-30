# VoltFix Dummy Data Management

This document explains how to use the management commands to add dummy data for testing the VoltFix application.

## Available Commands

### 1. Add Dummy Data
Adds comprehensive dummy data including service categories, services, product categories, and products.

```bash
# Add dummy data (will not overwrite existing data)
python manage.py add_dummy_data

# Clear existing data and add fresh dummy data
python manage.py add_dummy_data --clear
```

**What it creates:**
- **5 Service Categories**: Electrical Installation, Maintenance & Repair, Emergency Services, Inspection & Testing, Smart Home Setup
- **8 Services**: Complete Home Wiring, Circuit Breaker Installation, Outlet & Switch Installation, Electrical Troubleshooting, Light Fixture Installation, Emergency Power Restoration, Electrical Safety Inspection, Smart Thermostat Installation
- **5 Product Categories**: Lighting, Switches & Outlets, Circuit Protection, Smart Home, Tools & Equipment
- **11 Products**: LED Ceiling Light, Smart LED Bulb Pack, USB Outlet, GFCI Outlet, Circuit Breaker, Surge Protector Strip, Smart Thermostat, Smart Door Lock, Multimeter, Wire Stripper Set

### 2. Create Test User
Creates a test user account for testing authentication and booking functionality.

```bash
# Create default test user
python manage.py create_test_user

# Create custom test user
python manage.py create_test_user --username myuser --email myuser@example.com --password mypassword
```

**Default test user credentials:**
- Username: `testuser`
- Email: `test@example.com`
- Password: `testpass123`

## Testing the Application

### 1. Start the Development Server
```bash
python manage.py runserver
```

### 2. Access the Application
- **Home Page**: http://127.0.0.1:8000/
- **Services Page**: http://127.0.0.1:8000/services/
- **Products Page**: http://127.0.0.1:8000/products/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### 3. Test Service Booking
1. Login with the test user credentials
2. Navigate to the Services page
3. Click "Book Now" on any service
4. Fill in the booking form and submit
5. Check for success message

### 4. Test Product Features
1. Browse products on the Products page
2. Use category filters
3. Search for specific products
4. Add products to cart
5. View product details

## Data Structure

### Service Categories
Each service category includes:
- Name and description
- FontAwesome icon
- Color theme
- Related services

### Services
Each service includes:
- Name and detailed description
- Category association
- Price and duration
- Active status

### Product Categories
Each product category includes:
- Name and description
- FontAwesome icon
- Color theme
- Related products

### Products
Each product includes:
- Name and description
- Category association
- Price (with optional original price for discounts)
- Stock quantity
- Rating
- Featured status
- Condition (new/used/refurbished)

## Notes

- The `--clear` flag will delete all existing data before adding new dummy data
- Test user creation will skip if a user with the same username already exists
- All dummy data is realistic and suitable for demonstration purposes
- Images are not included in dummy data - you may want to add actual images for better visual appeal

## Troubleshooting

If you encounter issues:
1. Make sure all migrations are applied: `python manage.py migrate`
2. Check that the electric_services app is in INSTALLED_APPS
3. Verify that all models are properly imported
4. Check the Django console output for any error messages 