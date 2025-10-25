# Flippify

A platform for reselling items originally bought on marketplaces like eBay and Amazon.

## Overview

Flippify helps users track and manage their reselling business by providing:
- Item listing with purchase source tracking
- Automated price suggestions based on purchase source
- Sales tracking and profit calculation
- User reviews and ratings
- Analytics dashboard for sellers

## Features

- **Item Management**: List items with purchase details from eBay, Amazon, or other sources
- **Price Suggestions**: Automatic resale price recommendations based on purchase price and source
- **Sales Tracking**: Record sales and automatically calculate profits
- **Reviews System**: Users can leave reviews and ratings for items
- **Analytics**: Track total sales, revenue, profit, and inventory metrics per user

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. Visit API docs: http://localhost:8000/docs

## API Endpoints

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get a specific user

### Items
- `GET /items` - Get all items (supports filters: status, user_id)
- `POST /items` - Create a new item listing
- `GET /items/{id}` - Get a specific item
- `PUT /items/{id}` - Update an item
- `DELETE /items/{id}` - Delete an item

### Sales
- `GET /sales` - Get all sales (supports filter: item_id)
- `POST /sales` - Record a new sale
- `GET /sales/{id}` - Get a specific sale

### Reviews
- `GET /reviews` - Get all reviews (supports filters: item_id, user_id)
- `POST /reviews` - Create a new review
- `GET /reviews/{id}` - Get a specific review

### Analytics
- `GET /analytics/{user_id}` - Get analytics for a specific user
- `GET /analytics` - Get analytics for all users

### Health
- `GET /health` - Health check endpoint
- `GET /` - API information

## Database Schema

### Users
- id (Primary Key)
- username (Unique)
- email (Unique)
- created_at

### Items
- id (Primary Key)
- user_id (Foreign Key)
- title
- description
- purchase_source (eBay, Amazon, etc.)
- purchase_price
- resale_price
- suggested_price (auto-calculated)
- status (available, sold, pending)
- created_at
- updated_at

### Sales
- id (Primary Key)
- item_id (Foreign Key)
- sale_price
- sale_date
- buyer_name
- profit (auto-calculated)

### Reviews
- id (Primary Key)
- item_id (Foreign Key)
- user_id (Foreign Key)
- rating (1-5)
- comment
- created_at

### Analytics
- id (Primary Key)
- user_id (Foreign Key, Unique)
- total_sales
- total_revenue
- total_profit
- items_listed
- items_sold
- updated_at

## Example Usage

### Create a User

### Create an Item

### Record a Sale

### Create a Review

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application will automatically use the PORT environment variable provided by Render.

## Price Suggestion Algorithm

The system automatically suggests resale prices based on:
- **eBay items**: 30% markup
- **Amazon items**: 25% markup
- **Other sources**: 35% markup

These can be adjusted in the `calculate_suggested_price()` function.

## Development

The application uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **SQLite** for the database
- **Pydantic** for data validation
- **Uvicorn** as the ASGI server

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues or questions, please open an issue in the repository.