# Bro Connect

A social networking app focused on connecting male friends through common interests and activities.

## Overview

Bro Connect is a FastAPI-based backend service designed to facilitate friendships among men by connecting them through shared interests and activities. The platform provides features for profile creation, interest-based matchmaking, activity planning, messaging, and connection management.

## Features

- **User Management**: Create, read, update, and delete user profiles
- **Interest-Based Matching**: Find potential friends based on shared interests
- **Activity Planning**: Create and browse activities and events
- **Messaging**: Send and receive messages between connected users
- **Connection Management**: Send, accept, or reject connection requests
- **Interest Categories**: Manage and browse available interests

## Tech Stack

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

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. The API will be available at: `http://localhost:8000`

5. Visit the interactive API documentation: `http://localhost:8000/docs`

## API Endpoints

### Users

- `GET /users` - Get all users (with pagination)
- `POST /users` - Create a new user
- `GET /users/{id}` - Get a specific user by ID
- `PUT /users/{id}` - Update a user
- `DELETE /users/{id}` - Delete a user
- `GET /users/{id}/matches` - Get potential matches for a user based on interests

### Interests

- `GET /interests` - Get all interests
- `POST /interests` - Create a new interest

### Activities

- `GET /activities` - Get all activities (with optional user_id filter)
- `POST /activities` - Create a new activity
- `GET /activities/{id}` - Get a specific activity by ID

### Messages

- `POST /messages` - Send a message
- `GET /messages` - Get messages (with optional user_id filter)
- `GET /messages/conversation/{user1_id}/{user2_id}` - Get conversation between two users

### Connections

- `GET /connections` - Get connections (with optional filters)
- `POST /connections` - Create a new connection request
- `PUT /connections/{id}/status` - Update connection status (accept/reject)

### Utility

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `POST /seed-data` - Seed database with sample data (for testing)

## Database Schema

### Users
- id (Primary Key)
- name
- age
- bio
- created_at
- interests (Many-to-Many relationship)

### Interests
- id (Primary Key)
- name (Unique)

### Activities
- id (Primary Key)
- user_id (Foreign Key)
- activity_name
- date
- location
- description
- created_at

### Messages
- id (Primary Key)
- sender_id (Foreign Key)
- receiver_id (Foreign Key)
- content
- timestamp

### Connections
- id (Primary Key)
- user1_id (Foreign Key)
- user2_id (Foreign Key)
- status (pending/accepted/rejected)
- created_at

## Usage Examples

### Create a User


### Create an Activity


### Send a Message


### Find Matches


## Seed Data

To populate the database with sample data for testing:


This will create:
- 5 sample users
- 10 interest categories
- 3 sample activities
- 3 connection requests
- 3 sample messages

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application automatically uses the `PORT` environment variable provided by Render.

### Environment Variables

- `PORT` - Server port (default: 8000)

## CORS

CORS is enabled for all origins to facilitate frontend development. For production, consider restricting allowed origins in the CORS middleware configuration.

## Development

To run in development mode with auto-reload:


## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## License

MIT License

## Support

For issues and questions, please refer to the API documentation at `/docs` endpoint.