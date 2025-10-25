# Sup Boys

A community-driven social platform for connecting and engaging with like-minded individuals.

## Overview

Sup Boys is a modern social platform built with FastAPI and SQLite that enables users to create communities, share messages, start discussion threads, and plan events. It's designed for seamless community management and engagement.

## Features

- **Community Management**: Create and browse communities based on interests
- **Messaging**: Send text and multimedia messages within communities
- **Discussion Threads**: Start and participate in topic-based discussions
- **User Profiles**: Maintain user profiles with activity tracking
- **Event Planning**: Create and manage community events with calendar integration

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

Or run directly with Python:

4. Visit the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Users
- `GET /users` - Get all users
- `GET /users/{id}` - Get a specific user
- `POST /users` - Create a new user

### Communities
- `GET /communities` - Get all communities
- `GET /communities/{id}` - Get a specific community
- `POST /communities` - Create a new community

### Messages
- `GET /communities/{id}/messages` - Get all messages in a community
- `POST /communities/{id}/messages` - Post a message to a community

### Threads
- `GET /threads` - Get all threads (optional: filter by community_id)
- `GET /threads/{id}` - Get a specific thread
- `POST /threads` - Create a new discussion thread

### Events
- `GET /events` - Get all events (optional: filter by community_id)
- `GET /events/{id}` - Get a specific event
- `POST /events` - Create a new event

### Other
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Sample Data

The application automatically seeds the database with sample data on first run:
- 3 sample users
- 3 sample communities (Tech Talk, Gaming Squad, Fitness Crew)
- Sample messages, threads, and events

## API Usage Examples

### Create a Community

### Post a Message

### Create an Event

## Deployment

### Render.com

This application is ready to deploy on Render.com:

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Create a new Web Service on Render
3. Connect your repository
4. Use the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy!

The application automatically uses the PORT environment variable provided by Render.

## Database

The application uses SQLite with a file-based database (`supboys.db`). The database is automatically created on first run with the following schema:

- **Users**: user_id, username, email, profile_info, created_at
- **Communities**: community_id, name, description, created_at
- **Messages**: message_id, user_id, community_id, content, media_url, created_at
- **Threads**: thread_id, community_id, user_id, title, content, created_at
- **Events**: event_id, community_id, user_id, title, description, date_time, location, created_at

## CORS

CORS is enabled for all origins, making it easy to integrate with any frontend application.

## Development

To run in development mode with auto-reload:

## Production Considerations

For production deployment, consider:
- Adding authentication and authorization
- Implementing rate limiting
- Adding input sanitization
- Setting up proper logging
- Configuring CORS for specific origins
- Using a production-grade database (PostgreSQL, MySQL)
- Adding caching (Redis)
- Implementing WebSocket support for real-time messaging

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Support

For issues or questions, please open an issue in the repository.

---

Built with ❤️ using FastAPI