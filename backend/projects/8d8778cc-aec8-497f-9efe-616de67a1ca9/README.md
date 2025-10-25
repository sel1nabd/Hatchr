# SupBoys

A social networking app for men's communities to connect and share experiences.

## Overview

SupBoys is a social networking platform designed to help men's communities connect, share experiences, and build meaningful relationships. The platform provides features for user profiles, community groups, event creation, content sharing, and discussion forums.

## Features

- **User Profiles**: Create and manage user profiles with bio, location, and personal information
- **Community Groups**: Join and create groups based on interests and activities
- **Event Creation**: Organize and manage events with location, date, and attendee tracking
- **Content Sharing**: Share posts within groups or publicly
- **Discussion Forums**: Comment on posts and engage in discussions

## Tech Stack

- **Backend Framework**: FastAPI
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

4. Visit API docs: http://localhost:8000/docs

## API Endpoints

### Users
- `GET /users` - Get all users (with pagination)
- `GET /users/{user_id}` - Get a specific user
- `POST /users` - Create a new user

### Groups
- `GET /groups` - Get all groups (with pagination)
- `GET /groups/{group_id}` - Get a specific group
- `POST /groups` - Create a new group

### Events
- `GET /events` - Get all events (with pagination)
- `GET /events/{event_id}` - Get a specific event
- `POST /events` - Create a new event

### Posts
- `GET /posts` - Get all posts (with pagination)
- `GET /posts/{post_id}` - Get a specific post
- `POST /posts` - Create a new post

### Comments
- `GET /comments` - Get all comments (with pagination, optional post_id filter)
- `GET /comments/{comment_id}` - Get a specific comment
- `POST /comments` - Create a new comment

## API Documentation

Once the server is running, you can access:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Database Schema

### Users
- id (Primary Key)
- username (Unique)
- email (Unique)
- full_name
- bio
- location
- created_at

### Groups
- id (Primary Key)
- name (Unique)
- description
- category
- created_by
- member_count
- created_at

### Events
- id (Primary Key)
- title
- description
- location
- event_date
- created_by (Foreign Key to Users)
- group_id (Foreign Key to Groups, Optional)
- max_attendees
- current_attendees
- created_at

### Posts
- id (Primary Key)
- title
- content
- author_id (Foreign Key to Users)
- group_id (Foreign Key to Groups, Optional)
- likes
- created_at

### Comments
- id (Primary Key)
- content
- author_id (Foreign Key to Users)
- post_id (Foreign Key to Posts)
- likes
- created_at

## Example Usage

### Create a User

### Create a Group

### Create an Event

### Create a Post

### Create a Comment

## Deployment

### Render.com

This application is ready to deploy on Render.com free tier:

1. Push your code to a GitHub repository
2. Create a new Web Service on Render
3. Connect your repository
4. Render will automatically detect the Python environment
5. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy!

The application automatically uses the PORT environment variable provided by Render.

## Development

### Running in Development Mode

### Running in Production Mode

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.