# Flippify

A tool for flipping products on eBay and Amazon efficiently. Flippify helps users manage product sourcing, automated listing management, dynamic pricing, inventory synchronization, and sales analytics.

## Features

- **Product Sourcing**: Track products from eBay and Amazon with source pricing
- **Automated Listing Management**: Create and manage listings across platforms
- **Dynamic Pricing & Repricing**: Set pricing rules with markup percentages and fixed amounts
- **Inventory Synchronization**: Keep product quantities in sync across listings
- **Sales Analytics Dashboard**: Track sales performance, revenue, and profit

## Setup

1. Install dependencies:

2. Run the server:

3. Visit API docs: http://localhost:8000/docs

## API Endpoints

### Products
- `GET /products` - List all products (with optional filters)
- `POST /products` - Create a new product
- `GET /products/{id}` - Get a specific product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product

### Listings
- `GET /listings` - List all listings (with optional filters)
- `POST /listings` - Create a new listing
- `GET /listings/{id}` - Get a specific listing
- `PUT /listings/{id}` - Update a listing
- `DELETE /listings/{id}` - Delete a listing

### Pricing Rules
- `GET /pricing-rules` - List all pricing rules
- `POST /pricing-rules` - Create a new pricing rule
- `GET /pricing-rules/{id}` - Get a specific pricing rule
- `DELETE /pricing-rules/{id}` - Delete a pricing rule

### Sales Analytics
- `GET /sales-analytics` - List all sales records
- `POST /sales-analytics` - Create a new sales record
- `GET /sales-analytics/{id}` - Get a specific sales record

### Dashboard & Utilities
- `GET /dashboard/summary` - Get dashboard summary statistics
- `POST /inventory/sync` - Synchronize inventory across listings
- `POST /repricing/apply/{product_id}` - Apply pricing rules to a product

## Database Schema

### Users
- id, username, email, created_at

### Products
- id, user_id, title, description, source_platform, source_url, source_price, target_platform, category, sku, quantity, image_url, created_at, updated_at

### Listings
- id, user_id, product_id, platform, listing_id, title, description, price, quantity, status, listing_url, created_at, updated_at

### Pricing Rules
- id, product_id, rule_name, markup_percentage, markup_fixed, min_price, max_price, auto_reprice, competitor_price_check, created_at, updated_at

### Sales Analytics
- id, listing_id, sale_date, sale_price, quantity_sold, platform_fees, shipping_cost, profit, buyer_location, created_at

## Example Usage

### Create a Product

### Create a Listing

### Create a Pricing Rule

## Deployment

### Render.com
1. Create a new Web Service
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy

## Environment Variables

- `PORT` - Server port (default: 8000)

## License

MIT License