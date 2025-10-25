# Sup Boys

A social platform for fostering friendships and group activities, similar to Bumble BFF and Meetup.

## Features

- **User Management**: Create, read, update, and delete user profiles
- **Interest-Based Matching**: Find users with similar interests
- **Event Creation**: Create and manage group events
- **Event Discovery**: Browse and filter events by location
- **Chat Functionality**: Send messages between users
- **Profile Management**: Manage user bios, locations, and interests

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic
- **Documentation**: Auto-generated with Swagger UI

## Setup

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:

2. Install dependencies:

3. Run the server:

Or run directly:

4. Visit the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Users
- `GET /users` - Get all users with profiles and interests
- `POST /users` - Create a new user with optional profile
- `GET /users/{id}` - Get a specific user
- `PUT /users/{id}` - Update user information
- `DELETE /users/{id}` - Delete a user
- `GET /users/{id}/matches` - Find users with similar interests

### Events
- `GET /events` - Get all events (filterable by location)
- `POST /events` - Create a new event
- `GET /events/{id}` - Get a specific event
- `PUT /events/{id}` - Update an event
- `DELETE /events/{id}` - Delete an event

### Messages
- `GET /messages` - Get messages (filterable by user)
- `POST /messages` - Send a message
- `GET /messages/conversation/{user1_id}/{user2_id}` - Get conversation between two users

### Profiles
- `GET /profiles/{id}` - Get a specific profile

### Other
- `GET /` - API welcome message
- `GET /health` - Health check endpoint

## Example Usage

### Create a User with Profile and Interests

### Create an Event

### Send a Message

### Find Matches

## Database Schema

### Users
- id (Primary Key)
- name
- email (Unique)
- created_at

### Profiles
- id (Primary Key)
- user_id (Foreign Key to Users)
- bio
- location

### Interests
- id (Primary Key)
- profile_id (Foreign Key to Profiles)
- interest_name

### Events
- id (Primary Key)
- name
- description
- location
- date
- created_by (Foreign Key to Users)
- created_at

### Messages
- id (Primary Key)
- sender_id (Foreign Key to Users)
- receiver_id (Foreign Key to Users)
- content
- sent_at

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

The application automatically uses the `PORT` environment variable provided by Render.

## Development

### Running Tests

### Database Reset
To reset the database, simply delete the `supboys.db` file and restart the server. The database will be recreated automatically.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.