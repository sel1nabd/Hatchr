# Flippify

A platform for buying and selling flipped items quickly and efficiently.

## Overview

Flippify is a comprehensive marketplace platform that enables users to list, discover, and purchase flipped items. Built with FastAPI and SQLite, it provides a robust backend for managing users, items, categories, messages, and transactions.

## Features

- **User Management**: Create and manage user accounts
- **Item Listings**: Post items for sale with detailed descriptions, pricing, and categorization
- **Search & Discovery**: Advanced search with filters for category, price range, and keywords
- **Messaging System**: In-app messaging between buyers and sellers
- **Transaction Management**: Track purchases and sales with transaction history
- **Category Organization**: Organize items into predefined categories
- **Price Negotiation**: Communicate offers through the messaging system

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

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
- `GET /items` - Get all items (with optional filters)
  - Query parameters: `category_id`, `status`, `search`, `min_price`, `max_price`, `skip`, `limit`
- `POST /items` - Create a new item listing
- `GET /items/{id}` - Get a specific item
- `PUT /items/{id}` - Update an item
- `DELETE /items/{id}` - Delete an item

### Categories
- `GET /categories` - Get all categories
- `POST /categories` - Create a new category
- `GET /categories/{category_id}` - Get a specific category

### Messages
- `POST /messages` - Send a message
- `GET /messages/{item_id}` - Get all messages for an item
- `GET /messages/user/{user_id}` - Get all messages for a user

### Transactions
- `POST /transactions` - Create a new transaction
- `GET /transactions` - Get all transactions
- `GET /transactions/{transaction_id}` - Get a specific transaction
- `PUT /transactions/{transaction_id}/status` - Update transaction status

### Health
- `GET /health` - Check API health status
- `GET /` - API information

## Database Schema

### Users
- `id` (Integer, Primary Key)
- `name` (String)
- `email` (String, Unique)

### Items
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key)
- `title` (String)
- `description` (Text)
- `price` (Float)
- `category_id` (Integer, Foreign Key)
- `status` (String: available, sold, pending)
- `created_at` (DateTime)

### Messages
- `id` (Integer, Primary Key)
- `sender_id` (Integer, Foreign Key)
- `receiver_id` (Integer, Foreign Key)
- `item_id` (Integer, Foreign Key)
- `content` (Text)
- `timestamp` (DateTime)

### Categories
- `id` (Integer, Primary Key)
- `name` (String, Unique)

### Transactions
- `id` (Integer, Primary Key)
- `item_id` (Integer, Foreign Key)
- `buyer_id` (Integer, Foreign Key)
- `seller_id` (Integer, Foreign Key)
- `price` (Float)
- `status` (String: pending, completed, cancelled)
- `timestamp` (DateTime)

## Default Categories

The system comes pre-loaded with the following categories:
- Electronics
- Clothing
- Home & Garden
- Sports & Outdoors
- Toys & Games
- Books
- Collectibles
- Furniture
- Other

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application automatically uses the `PORT` environment variable provided by Render.

## Development

### Running Tests
The API documentation at `/docs` provides an interactive interface to test all endpoints.

### Environment Variables
- `PORT` - Server port (default: 8000)

## API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Create a User

### Create an Item

### Search Items

### Send a Message

## License

MIT License

## Support

For issues and questions, please refer to the API documentation at `/docs` or check the health endpoint at `/health`.