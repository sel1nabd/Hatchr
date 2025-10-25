# KickStart Africa

An online platform to sell affordable, durable footballs for kids in Africa.

## Overview

KickStart Africa is a FastAPI-based e-commerce platform designed to provide affordable and durable footballs to children across Africa. The platform focuses on product quality, affordability, and ease of use.

## Features

- **Product Catalog**: Browse a wide selection of durable footballs
- **User Management**: Create and manage user accounts
- **Order Processing**: Simple checkout process with real-time inventory updates
- **Inventory Management**: Track stock levels and availability
- **Durability Ratings**: Products rated for quality and longevity
- **Price Optimization**: Affordable pricing tailored for African markets

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite (file-based)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **CORS**: Enabled for all origins

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

Or run directly:

4. Visit the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Products
- `GET /products` - List all products (with optional filters)
- `GET /products/{id}` - Get a specific product
- `POST /products` - Create a new product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product

### Orders
- `GET /orders` - List all orders (with optional filters)
- `GET /orders/{id}` - Get a specific order
- `POST /orders` - Create a new order
- `PATCH /orders/{id}/status` - Update order status

### Users
- `GET /users` - List all users
- `GET /users/{id}` - Get a specific user
- `POST /users` - Create a new user

### Inventory
- `GET /inventory` - List all inventory records
- `GET /inventory/{product_id}` - Get inventory for a product
- `PUT /inventory/{product_id}` - Update inventory quantity

### Other
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Sample Data

The application comes pre-loaded with sample data including:
- 3 sample users
- 5 football products with varying prices and durability ratings
- Corresponding inventory records

## Query Parameters

### Products
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return
- `min_price`: Filter by minimum price
- `max_price`: Filter by maximum price
- `in_stock`: Filter by stock availability (true/false)

### Orders
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum number of records to return
- `user_id`: Filter by user ID
- `status`: Filter by order status

## Order Status Values

- `pending`: Order placed but not confirmed
- `confirmed`: Order confirmed and being processed
- `shipped`: Order has been shipped
- `delivered`: Order delivered to customer
- `cancelled`: Order cancelled

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application automatically uses the PORT environment variable provided by Render.

### Environment Variables

- `PORT`: Server port (default: 8000)

## Database

The application uses SQLite with a file-based database (`kickstart_africa.db`). The database is automatically created on first run with the following tables:

- **users**: User account information
- **products**: Football product catalog
- **orders**: Customer orders
- **inventory**: Stock management

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## CORS

CORS is enabled for all origins, making the API accessible from any frontend application.

## Development

To run in development mode with auto-reload:

## Production Considerations

For production deployment:
1. Consider migrating to PostgreSQL for better performance
2. Implement authentication and authorization
3. Add rate limiting
4. Set up proper logging and monitoring
5. Use environment variables for sensitive configuration
6. Implement caching for frequently accessed data
7. Add payment gateway integration

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.