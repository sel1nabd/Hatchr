# FinCRM

A financial CRM tool for businesses to manage financial interactions and customer relationships.

## Overview

FinCRM is a simple, file-based SQLite-backed application built with FastAPI that helps businesses manage customer relationships with a financial focus. It provides essential features for tracking customers, financial transactions, reports, tasks, and appointments.

## Features

- **Customer Profile Management**: Create, read, update, and delete customer profiles with contact information, company details, and notes
- **Financial Transaction Tracking**: Track all financial transactions associated with customers including date, amount, type, and description
- **Customizable Financial Reports**: Generate and store financial reports for customers
- **Task Management**: Create and track tasks related to customers with due dates and status tracking
- **Appointment Scheduling**: Schedule and manage appointments with customers

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite (file-based)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository or download the source code

2. Install dependencies:

3. Run the server:

4. Visit API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Customers

- `GET /customers` - Get all customers (with pagination)
- `POST /customers` - Create a new customer
- `GET /customers/{id}` - Get a specific customer by ID
- `PUT /customers/{id}` - Update a customer
- `DELETE /customers/{id}` - Delete a customer

### Transactions

- `GET /transactions` - Get all transactions (with pagination and optional customer_id filter)
- `POST /transactions` - Create a new transaction
- `GET /transactions/{id}` - Get a specific transaction by ID
- `PUT /transactions/{id}` - Update a transaction
- `DELETE /transactions/{id}` - Delete a transaction

### Reports

- `GET /reports` - Get all reports (with pagination and optional customer_id filter)
- `POST /reports` - Create a new report

### Tasks

- `GET /tasks` - Get all tasks (with pagination and optional filters)
- `POST /tasks` - Create a new task

### Appointments

- `GET /appointments` - Get all appointments (with pagination and optional customer_id filter)
- `POST /appointments` - Create a new appointment

### Utility

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Database Schema

### Customers Table
- `id` (Integer, Primary Key)
- `name` (String, Required)
- `contact_info` (String, Optional)
- `company` (String, Optional)
- `notes` (Text, Optional)

### Transactions Table
- `id` (Integer, Primary Key)
- `customer_id` (Integer, Foreign Key, Required)
- `date` (DateTime, Required)
- `amount` (Float, Required)
- `type` (String, Required)
- `description` (Text, Optional)

### Reports Table
- `id` (Integer, Primary Key)
- `customer_id` (Integer, Foreign Key, Required)
- `report_type` (String, Required)
- `content` (Text, Optional)
- `created_at` (DateTime, Auto-generated)

### Tasks Table
- `id` (Integer, Primary Key)
- `customer_id` (Integer, Foreign Key, Required)
- `task_description` (Text, Required)
- `due_date` (DateTime, Optional)
- `status` (String, Default: "pending")

### Appointments Table
- `id` (Integer, Primary Key)
- `customer_id` (Integer, Foreign Key, Required)
- `date_time` (DateTime, Required)
- `location` (String, Optional)
- `notes` (Text, Optional)

## Example Usage

### Create a Customer


### Create a Transaction


### Get All Customers


### Update a Customer


### Delete a Transaction


## Deployment

### Render.com Deployment

This application is ready to deploy on Render.com free tier:

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Create a new Web Service on Render.com
3. Connect your repository
4. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy!

The application automatically uses the PORT environment variable provided by Render.

## CORS

CORS is enabled for all origins, allowing the API to be accessed from any frontend application.

## Development

To run in development mode with auto-reload:


## Production Considerations

For production deployment, consider:

- Adding authentication and authorization
- Implementing rate limiting
- Adding input validation and sanitization
- Setting up proper logging
- Configuring environment-specific settings
- Adding database migrations
- Implementing backup strategies
- Setting up monitoring and alerting

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.