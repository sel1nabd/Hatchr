# Flippify

A platform for flipping products on eBay and Amazon. Flippify helps users discover profitable products, track prices, calculate profit margins, and analyze sales performance.

## Features

- **Product Management**: Add, update, and track products from various sources
- **Price Tracking**: Monitor price history and trends across platforms
- **Profit Calculation**: Automatic profit margin and net profit calculations
- **Sales Analytics**: Comprehensive sales reporting and analytics
- **Alert System**: Set up custom alerts for price changes and product events
- **Multi-User Support**: Manage multiple users and their product portfolios

## Setup

### Local Development

1. **Install dependencies**:

2. **Run the server**:

3. **Visit API docs**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Production Deployment (Render.com)

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

## API Endpoints

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get a specific user

### Products
- `GET /products` - Get all products (supports filtering by user_id, status, category)
- `POST /products` - Create a new product
- `GET /products/{id}` - Get a specific product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product

### Price History
- `GET /price-history/{product_id}` - Get price history for a product
- `POST /price-history` - Add a new price history entry

### Sales
- `GET /sales` - Get all sales (supports filtering by user_id, product_id, platform)
- `POST /sales` - Record a new sale
- `GET /sales/{sale_id}` - Get a specific sale
- `GET /sales/analytics/summary` - Get sales analytics and summary

### Alerts
- `GET /alerts` - Get all alerts (supports filtering by user_id, is_active)
- `POST /alerts` - Create a new alert
- `GET /alerts/{alert_id}` - Get a specific alert
- `PUT /alerts/{alert_id}` - Update an alert (activate/deactivate)
- `DELETE /alerts/{alert_id}` - Delete an alert

### System
- `GET /` - API information
- `GET /health` - Health check endpoint

## Database Schema

### Users
- User information and account details

### Products
- Product details including source and target platforms
- Pricing information (source price, target price, current price)
- SKU, quantity, and status tracking
- Automatic profit margin calculation

### PriceHistory
- Historical pricing data for products
- Platform-specific price tracking
- Timestamp-based records

### Sales
- Sales transactions with detailed profit calculations
- Platform fees and shipping costs
- Net profit tracking
- Order ID and notes

### Alerts
- User-defined alerts for price changes and product events
- Configurable thresholds and conditions
- Active/inactive status tracking

## Example Usage

### Create a User

### Add a Product

### Record a Sale

### Get Sales Analytics

### Create a Price Alert

## Profit Calculation

The system automatically calculates:
- **Profit Margin**: `((target_price - source