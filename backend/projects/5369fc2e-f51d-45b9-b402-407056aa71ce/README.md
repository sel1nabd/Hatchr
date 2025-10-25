# Flippify

A platform for users to easily flip and resell items on eBay and similar sites.

## Overview

Flippify helps users manage their reselling business by providing tools for:
- Item listing management
- Automatic pricing suggestions based on market data
- Sales tracking and analytics
- Market trend analysis
- Integration with platforms like eBay, Mercari, Poshmark, and OfferUp

## Features

- **Item Management**: Create, read, update, and delete item listings
- **Smart Pricing**: Automatic price suggestions based on purchase price and category
- **Sales Tracking**: Record and track all your sales with profit calculations
- **Analytics Dashboard**: View comprehensive analytics including revenue, profit margins, and trends
- **Market Trends**: Analyze market trends and category performance over time
- **Multi-Platform Support**: Manage items across different selling platforms

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. Visit the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get a specific user

### Platforms
- `POST /platforms` - Create a new platform
- `GET /platforms` - Get all platforms

### Items
- `GET /items` - Get all items (supports filters: status, category, user_id)
- `POST /items` - Create a new item
- `GET /items/{id}` - Get a specific item
- `PUT /items/{id}` - Update an item
- `DELETE /items/{id}` - Delete an item

### Sales
- `GET /sales` - Get all sales (supports filter: user_id)
- `POST /sales` - Create a new sale
- `GET /sales/{id}` - Get a specific sale

### Analytics
- `GET /analytics` - Get analytics overview (total items, sales, revenue, profit, etc.)
- `GET /analytics/trends` - Get market trends and pricing data

## Database Schema

### Users
- id (Primary Key)
- username (Unique)
- email (Unique)
- created_at

### Platforms
- id (Primary Key)
- name (Unique)
- api_key
- is_active
- created_at

### Items
- id (Primary Key)
- title
- description
- purchase_price
- suggested_price
- listing_price
- category
- condition
- status (available, listed, sold)
- user_id (Foreign Key)
- platform_id (Foreign Key)
- created_at
- updated_at

### Sales
- id (Primary Key)
- item_id (Foreign Key)
- user_id (Foreign Key)
- sale_price
- fees
- profit
- sale_date
- buyer_info
- notes

### Analytics
- id (Primary Key)
- category
- metric_name
- metric_value
- period
- recorded_at
- metadata

## Example Usage

### Create an Item

### Record a Sale

### Get Analytics

## Deployment

### Render.com

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

The application will automatically use the PORT environment variable provided by Render.

## Sample Data

The application comes with sample data including:
- A demo user (demo@flippify.com)
- Four platforms (eBay, Mercari, Poshmark, OfferUp)
- Three sample items
- One sample sale

## Technologies Used

- **FastAPI**: Modern, fast