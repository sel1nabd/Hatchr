# AdvisorConnect

A streamlined CRM specifically designed for financial advisors to manage client relationships, track financial accounts, automate tasks and workflows, manage documents, and generate reports.

## Features

- **Client Management**: Complete CRUD operations for managing client information
- **Financial Account Tracking**: Track multiple accounts per client with balances and account types
- **Task and Workflow Automation**: Create and manage tasks with due dates for each client
- **Document Management**: Store and organize client documents with upload tracking
- **Reporting and Analytics**: Generate and store various report types for clients

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite (file-based)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. Visit API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Clients
- `GET /clients` - Retrieve all clients (with pagination)
- `POST /clients` - Create a new client
- `GET /clients/{id}` - Get a specific client
- `PUT /clients/{id}` - Update a client
- `DELETE /clients/{id}` - Delete a client

### Accounts
- `GET /accounts` - Retrieve all accounts (with optional client_id filter)
- `POST /accounts` - Create a new account
- `GET /accounts/{id}` - Get a specific account
- `PUT /accounts/{id}` - Update an account
- `DELETE /accounts/{id}` - Delete an account

### Tasks
- `GET /tasks` - Retrieve all tasks (with optional client_id filter)
- `POST /tasks` - Create a new task
- `GET /tasks/{id}` - Get a specific task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

### Documents
- `GET /documents` - Retrieve all documents (with optional client_id filter)
- `POST /documents` - Create a new document record
- `GET /documents/{id}` - Get a specific document
- `DELETE /documents/{id}` - Delete a document record

### Reports
- `GET /reports` - Retrieve all reports (with optional client_id filter)
- `POST /reports` - Create a new report
- `GET /reports/{id}` - Get a specific report
- `DELETE /reports/{id}` - Delete a report

### Utility
- `GET /` - Welcome message and API information
- `GET /health` - Health check endpoint

## Database Schema

### Clients Table
- `client_id` (Primary Key)
- `name` (String, required)
- `email` (String, unique, required)
- `phone` (String, required)

### Accounts Table
- `account_id` (Primary Key)
- `client_id` (Foreign Key → Clients)
- `account_type` (String, required)
- `balance` (Float, required)

### Tasks Table
- `task_id` (Primary Key)
- `client_id` (Foreign Key → Clients)
- `description` (String, required)
- `due_date` (Date, required)

### Documents Table
- `document_id` (Primary Key)
- `client_id` (Foreign Key → Clients)
- `filename` (String, required)
- `upload_date` (DateTime, auto-generated)

### Reports Table
- `report_id` (Primary Key)
- `client_id` (Foreign Key → Clients)
- `report_type` (String, required)
- `created_at` (DateTime, auto-generated)

## Example Usage

### Create a Client

### Create an Account for a Client

### Create a Task

## Deployment

### Render.com Deployment

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application will automatically use the PORT environment variable provided by Render.

## Development

### Running in Development Mode

### Running in Production Mode

## CORS

CORS is enabled for all origins in this MVP version. For production use, configure specific allowed origins in the CORS middleware settings.

## Notes

- This is an MVP version without authentication
- SQLite database file (`advisorconnect.db`) will be created automatically on first run
- All timestamps are stored in UTC
- Deleting a client will cascade delete all associated accounts, tasks, documents, and reports

## License

MIT License - Feel free to use this project for your own purposes.

## Support

For issues and questions, please refer to the API documentation at `/docs` endpoint.