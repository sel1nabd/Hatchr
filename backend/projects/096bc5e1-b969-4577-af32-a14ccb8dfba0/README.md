# F-Tracker

A simple personal finance tracking application that allows users to track their expenses, create and monitor budgets, and gain insights into their spending habits.

## Features

- **Expense Tracking**: Record and manage all your expenses with categories, dates, and descriptions
- **Budget Management**: Create budgets for different categories and time periods
- **Spending Insights**: Get detailed reports on your spending patterns and category-wise breakdowns
- **Budget Monitoring**: Track budget usage with real-time status updates
- **Category Management**: Organize expenses and budgets by customizable categories

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. Visit API docs: http://localhost:8000/docs

The application will automatically create an SQLite database (`ftracker.db`) and initialize it with default categories and a demo user.

## API Endpoints

### Users
- `GET /users` - Get all users
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get a specific user

### Categories
- `GET /categories` - Get all categories
- `POST /categories` - Create a new category

### Expenses
- `GET /expenses` - Get all expenses (supports filtering by user_id, category_id, date range)
- `POST /expenses` - Create a new expense
- `GET /expenses/{id}` - Get a specific expense
- `PUT /expenses/{id}` - Update an expense
- `DELETE /expenses/{id}` - Delete an expense

### Budgets
- `GET /budgets` - Get all budgets (supports filtering by user_id, category_id, active status)
- `POST /budgets` - Create a new budget
- `GET /budgets/{id}` - Get a specific budget
- `PUT /budgets/{id}` - Update a budget
- `DELETE /budgets/{id}` - Delete a budget
- `GET /budgets/{id}/status` - Get budget status with spending information

### Insights
- `GET /insights/spending` - Get spending report for a user within a date range

### Health
- `GET /health` - Health check endpoint
- `GET /` - API information

## Usage Examples

### Creating an Expense

### Creating a Budget

### Getting Spending Insights

## Default Categories

The application comes with the following pre-configured categories:
- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Education
- Travel
- Personal Care
- Other

## Database Schema

### Users
- `id`: Integer (Primary Key)
- `name`: String
- `email`: String (Unique)

### Categories
- `id`: Integer (Primary Key)
- `name`: String (Unique)

### Expenses
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `amount`: Float
- `category_id`: Integer (Foreign Key)
- `date`: Date
- `description`: String (Optional)

### Budgets
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `category_id`: Integer (Foreign Key)
- `amount`: Float
- `period_start`: Date
- `period_end`: Date

## Deployment

### Render.com

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

The application will automatically use the PORT environment variable provided by Render.

## Development

To run in development mode with auto-reload:

Or using uvicorn directly:

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please refer to the project repository.