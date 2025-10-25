# DevFinance CRM

A financial CRM tailored for software developers to manage their finances and client interactions.

## Overview

DevFinance CRM is a comprehensive financial management solution designed specifically for software developers who juggle multiple clients and projects. It provides essential features for managing clients, tracking expenses, creating invoices, managing projects, and generating financial reports.

## Features

- **Client Management**: Store and manage client contact information, company details, and notes
- **Invoice Management**: Create, track, and manage invoices with multiple status options (pending, paid, overdue, cancelled)
- **Expense Tracking**: Record and categorize business expenses with receipt tracking
- **Project Time Tracking**: Manage projects with hourly rates, time tracking, and budget management
- **Financial Reporting**: Get comprehensive financial insights including revenue, expenses, and net income
- **User Management**: Support for multiple users (developers) on the platform

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: SQLite (file-based, no external dependencies)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **API Documentation**: Auto-generated with Swagger UI

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. The API will be available at: `http://localhost:8000`

5. Visit the interactive API documentation: `http://localhost:8000/docs`

### Environment Variables

- `PORT`: Server port (default: 8000)

Example:

## API Endpoints

### Root
- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint

### Clients
- `GET /clients` - Get all clients (supports pagination)
- `POST /clients` - Create a new client
- `GET /clients/{id}` - Get a specific client
- `PUT /clients/{id}` - Update a client
- `DELETE /clients/{id}` - Delete a client

### Invoices
- `GET /invoices` - Get all invoices (supports filtering by status and client_id)
- `POST /invoices` - Create a new invoice
- `GET /invoices/{id}` - Get a specific invoice
- `PUT /invoices/{id}` - Update invoice status

### Expenses
- `GET /expenses` - Get all expenses (supports filtering by category)
- `POST /expenses` - Create a new expense
- `GET /expenses/{id}` - Get a specific expense
- `DELETE /expenses/{id}` - Delete an expense

### Projects
- `GET /projects` - Get all projects (supports filtering by status and client_id)
- `POST /projects` - Create a new project
- `GET /projects/{id}` - Get a specific project
- `PUT /projects/{id}` - Update a project
- `DELETE /projects/{id}` - Delete a project

### Financial Reporting
- `GET /financial-report` - Get comprehensive financial report including revenue, expenses, and net income

### Users
- `GET /users` - Get all users
- `POST /users` - Create a new user
- `GET /users/{id}` - Get a specific user

## Database Schema

### Users
- id (Primary Key)
- name
- email (Unique)
- phone
- company
- created_at

### Clients
- id (Primary Key)
- user_id (Foreign Key)
- name
- email
- phone
- company
- address
- notes
- created_at

### Invoices
- id (Primary Key)
- user_id (Foreign Key)
- client_id (Foreign Key)
- invoice_number (Unique)
- amount
- status (pending, paid, overdue, cancelled)
- issue_date
- due_date
- description
- notes
- created_at

### Expenses
- id (Primary Key)
- user_id (Foreign Key)
- category
- amount
- description
- date
- receipt_url
- notes
- created_at

### Projects
- id (Primary Key)
- user_id (Foreign Key)
- client_id (Foreign Key)
- name
- description
- status (active, completed, on_hold, cancelled)
- hourly_rate
- hours_tracked
- budget
- start_date
- end_date
- created_at

## Usage Examples

### Create a Client

### Create an Invoice

### Create an Expense