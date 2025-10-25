# Sup Boys Network

A social networking platform designed to connect young men based on shared interests and activities. This MVP provides core functionalities including user profiles, community forums, content sharing, event management, and real-time messaging.

## Features

- **User Management**: Create, read, update, and delete user profiles
- **Community Forums**: Post content and engage in discussions through comments
- **Content Sharing**: Share posts with the community
- **Event Management**: Create and manage events with date and time
- **Real-time Messaging**: Send direct messages between users

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Database Schema

### Users
- id (Primary Key)
- username (Unique)
- email (Unique)
- bio (Optional)

### Posts
- id (Primary Key)
- user_id (Foreign Key → Users)
- content
- timestamp

### Comments
- id (Primary Key)
- post_id (Foreign Key → Posts)
- user_id (Foreign Key → Users)
- content
- timestamp

### Events
- id (Primary Key)
- user_id (Foreign Key → Users)
- name
- description (Optional)
- date
- time

### Messages
- id (Primary Key)
- sender_id (Foreign Key → Users)
- receiver_id (Foreign Key → Users)
- content
- timestamp

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the files

2. Install dependencies:

3. Run the server:

4. The API will be available at: `http://localhost:8000`

5. Access the interactive API documentation at: `http://localhost:8000/docs`

## API Endpoints

### Users
- `GET /users` - Get all users (with pagination)
- `POST /users` - Create a new user
- `GET /users/{id}` - Get a specific user
- `PUT /users/{id}` - Update a user
- `DELETE /users/{id}` - Delete a user

### Posts
- `GET /posts` - Get all posts (with pagination and optional user_id filter)
- `POST /posts` - Create a new post
- `GET /posts/{id}` - Get a specific post
- `DELETE /posts/{id}` - Delete a post

### Comments
- `GET /comments` - Get all comments (with optional post_id or user_id filter)
- `POST /comments` - Create a new comment
- `DELETE /comments/{id}` - Delete a comment

### Events
- `GET /events` - Get all events (with pagination and optional user_id filter)
- `POST /events` - Create a new event
- `GET /events/{id}` - Get a specific event
- `DELETE /events/{id}` - Delete an event

### Messages
- `GET /messages` - Get all messages (with optional sender_id or receiver_id filter)
- `POST /messages` - Create a new message
- `GET /messages/{id}` - Get a specific message
- `DELETE /messages/{id}` - Delete a message

### Health
- `GET /health` - Health check endpoint

## Usage Examples

### Create a User

### Create a Post

### Create an Event

### Send a Message

## Deployment

### Render.com Deployment

1. Create a new Web Service on Render.com
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

The application will automatically use the PORT environment variable provided by Render.

## Development

### Running in Development Mode

### Running in Production Mode

## CORS

CORS is enabled for all origins, making it easy to connect from any frontend application.

## Database

The application uses SQLite with a file-based database (`supboys.db`). The database is automatically created on first run with all necessary tables.

## API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## License

This is an MVP/demo project for educational purposes.

## Support

For issues or questions, please refer to the API documentation at `/docs` endpoint.