# DevFinance CRM

A financial CRM tailored for developers to manage client financial interactions efficiently.

## Overview

DevFinance CRM is a specialized financial management system designed for freelance developers and development agencies. It provides comprehensive tools for managing clients, projects, invoices, payments, and expenses in one unified platform.

## Features

- **Client Management**: Store and manage client information including contact details and company information
- **Invoice Generation**: Create, track, and manage invoices with automatic total calculation
- **Payment Tracking**: Record and monitor payments against invoices with status tracking
- **Project Management**: Organize work by projects with budget tracking and status management
- **Expense Tracking**: Log expenses associated with projects for accurate profit calculation
- **Financial Overviews**: Get comprehensive financial summaries for projects and clients

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. Visit API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Clients
- `GET /clients` - List all clients
- `