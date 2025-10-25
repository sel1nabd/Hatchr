# FinanceSync

A streamlined CRM tailored for financial professionals. FinanceSync provides comprehensive client management, financial data tracking, task automation, reporting, and document management capabilities designed specifically for wealth management and financial advisory firms.

## Features

- **Client Management**: Complete CRUD operations for managing client information including contact details, risk profiles, and demographic data
- **Financial Data Integration**: Track portfolio values, annual income, net worth, investment goals, and asset allocation
- **Task & Workflow Automation**: Create and manage tasks with priorities, due dates, and status tracking
- **Reporting & Analytics**: Generate and store various report types with customizable data and time periods
- **Document Management**: Organize and track client documents with metadata

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLite (file-based)
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Server**: Uvicorn 0.24.0

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the source code

2. Install dependencies:

3. Run the server:

4. Visit API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Clients
- `GET /clients` - Retrieve all clients (with pagination)
- `POST /clients` - Create a new client
- `GET /clients/{client_id}` - Get a specific client
- `PUT /clients/{client_id}` - Update a client
- `DELETE /clients/{client_id}` - Delete a client

### Financial Data
- `GET /financial-data` - Retrieve financial data (filterable by client_id)
- `POST /financial-data` - Create new financial data entry
- `GET /financial-data/{data_id}` - Get specific financial data

### Tasks
- `GET /tasks` - Retrieve tasks (filterable by client_id and status)
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task

### Reports
- `GET /reports` - Retrieve reports (filterable by client_id and report_type)
- `POST /reports` - Create a new report
- `GET /reports/{report_id}` - Get a specific report

### Documents
- `GET /documents` - Retrieve documents (filterable by client_id)
- `POST /documents` - Create a new document entry
- `GET /documents/{document_id}` - Get a specific document
- `DELETE /documents/{document_id}` - Delete a document

### Utility
- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint

## Database Schema

### Clients Table
- `client_id` (Primary Key)
- `name`, `email`, `phone`, `address`
- `date_of_birth`, `occupation`, `risk_profile`
- `created_at`, `updated_at`

### Financial Data Table
- `data_id` (Primary Key)
- `client_id` (Foreign Key)
- `portfolio_value`, `annual_income`, `net_worth`
- `investment_goals`, `asset_allocation`
- `last_updated`, `created_at`

### Tasks Table
- `task_id` (Primary Key)
- `client_id` (Foreign Key)
- `title`, `description`, `due_date`
- `status`, `priority`, `assigned_to`
- `created_at`, `completed_at`

### Reports Table
- `report_id` (Primary Key)
- `client_id` (Foreign Key)
- `report_type`, `report_name`, `data`
- `generated_at`, `period_start`, `period_end`

### Documents Table
- `document_id` (Primary Key)
- `client_id` (Foreign Key)
- `file_name`, `file_path`, `file_type`
- `file_size`, `description`, `uploaded_at`

## Example Usage

### Create a Client

### Add Financial Data

### Create a Task

## Deployment

### Render.com Deployment

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application automatically uses the PORT environment variable provided by Render.

### Environment Variables
- `PORT` - Server port (default: 8000)

## Development

### Running in Development Mode

### Running in Production Mode

## Data Validation

The API includes comprehensive validation:
- Email format validation
- Required field enforcement
- Data type validation
- Foreign key integrity checks
- Unique constraint enforcement (e.g., client emails)

## CORS Configuration

CORS is enabled for all origins to facilitate frontend integration. In production, consider restricting this to specific domains.

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.

---

**FinanceSync** - Empowering financial professionals with streamlined client relationship management.