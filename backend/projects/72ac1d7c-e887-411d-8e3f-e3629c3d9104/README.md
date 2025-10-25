# Flipify

A tool to streamline and optimize the process of reselling products on eBay.

## Overview

Flipify is a comprehensive backend solution for e-commerce resellers, providing automated listing creation, inventory management, price optimization, and sales analytics. Built with FastAPI and SQLite, it offers a lightweight yet powerful platform for managing your resale business.

## Features

- **Automated eBay Listing Creation**: Create listings with automatic price optimization
- **Inventory Management**: Track items available for resale with SKU-based organization
- **Price Optimization**: Intelligent pricing algorithm based on purchase price and category
- **Sales Analytics**: Comprehensive tracking of sales performance and profitability
- **Cross-Platform Support**: Ready for multi-platform expansion beyond eBay

## Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. Visit API documentation:

## API Endpoints

### Listings
- `GET /listings` - Get all listings (supports filtering by status)
- `POST /listings` - Create a new listing with automatic price optimization
- `GET /listings/{id}` - Get a specific listing
- `PUT /listings/{id}` - Update a listing
- `DELETE /listings/{id}` - Delete a listing

### Inventory
- `GET /inventory` - Get all inventory items
- `POST /inventory` - Add a new inventory item
- `GET /inventory/{id}` - Get a specific inventory item

### Sales
- `GET /sales` - Get all sales records
- `POST /sales` - Record a new sale

### Analytics
- `GET /analytics` - Get comprehensive analytics summary
- `GET /analytics/detailed` - Get detailed analytics records

## Database Schema

### Users
- id, username, email, created_at

### Listings
- id, user_id, inventory_id, title, description, price, optimized_price, category, condition, platform, status, ebay_listing_id, created_at, updated_at

### Inventory
- id, user_id, sku, name, description, purchase_price, quantity, category, condition, location, status, created_at, updated_at

### Sales
- id, user_id, listing_id, inventory_id, sale_price, purchase_price, profit, platform, buyer_info, sale_date, created_at

### Analytics
- id, user_id, metric_name, metric_value, metric_type, period, created_at

## Usage Examples

### Create a Listing

### Add Inventory Item

### Record a Sale

### Get Analytics

## Deployment

### Render.com

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application will automatically use the PORT environment variable provided by Render.

## Price Optimization

The built-in price optimization algorithm considers:
- Base profit margin (30%)
- Category-specific multipliers:
  - Electronics: 1.2x
  - Clothing: 1.5x
  - Collectibles: 1.8x
  - Books: 1.3x
  - Toys: 1.4x

## Development

### Running Tests

### Database Reset
To reset the database, simply delete the `flipify.db` file and restart the server.

## License

MIT License - Feel free to use this project for your resale business.

## Support

For issues and questions, please refer to the API documentation at `/docs` endpoint.