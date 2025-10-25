# Flippify

A platform for facilitating the flipping of products on eBay and Amazon.

## Overview

Flippify is a comprehensive platform designed to assist users in the flipping of products on eBay and Amazon. It provides inventory management, automated listing creation, price optimization, sales analytics, and purchase/sales tracking.

## Features

- **Inventory Management**: Track all products with purchase details, quantities, and categories
- **Listing Management**: Create and manage listings across eBay and Amazon
- **Price Optimization**: Get intelligent price suggestions based on costs and platform fees
- **Sales Analytics**: Comprehensive dashboard with revenue, profit, and margin tracking
- **Transaction Tracking**: Monitor all purchases and sales with detailed records

## Setup

### Local Development

1. Install dependencies:

2. Run the server:

3. Visit API docs: http://localhost:8000/docs

### Production Deployment (Render.com)

1. Push code to GitHub repository
2. Create new Web Service on Render.com
3. Connect your repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy!

## API Endpoints

### Products
- `GET /products` - Get all products (supports filtering by category)
- `POST /products` - Create a new product
- `GET /products/{id}` - Get a specific product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product

### Listings
- `GET /listings` - Get all listings (supports filtering by platform and status)
- `POST /listings` - Create a new listing
- `GET /listings/{id}` - Get a specific listing
- `PUT /listings/{id}` - Update a listing
- `DELETE /listings/{id}` - Delete a listing

### Sales
- `GET /sales` - Get all sales
- `POST /sales` - Record a new sale
- `GET /sales/{id}` - Get a specific sale

### Analytics & Optimization
- `GET /analytics` - Get comprehensive sales analytics dashboard
- `GET /listings/{id}/price-suggestion` - Get price optimization suggestions

### Utility
- `GET /` - API welcome message
- `GET /health` - Health check endpoint

## Database Schema

### Users
- id, username, email, created_at

### Products
- id, name, description, purchase_price, purchase_date, purchase_source
- quantity, category, condition, sku, user_id, created_at, updated_at

### Listings
- id, product_id, platform, title, description, listing_price
- status, listing_url, listing_date, user_id, created_at, updated_at

### Sales
- id, listing_id, sale_price, sale_date, buyer_info
- shipping_cost, platform_fees, profit, created_at

### Transactions
- id, user_id, transaction_type, amount, description
- transaction_date, created_at

## Example Usage

### Create a Product

### Create a Listing

### Record a Sale

### Get Analytics

### Get Price Suggestion

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic
- **Server**: Uvicorn

## Environment Variables

- `PORT` - Server port (default: 8000)

## License

MIT License

## Support

For issues and questions, please open an issue on the GitHub repository.