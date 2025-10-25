# TeamTask Pro

A task management application for remote teams with real-time collaboration, task boards, and integrated team chat.

## Features

- **Task Boards**: Create and manage multiple task boards for different projects
- **Task Management**: Full CRUD operations for tasks with status tracking, due dates, and assignments
- **Team Collaboration**: Integrated chat system for team communication
- **User Management**: Track users and assign tasks to team members
- **Chat Rooms**: Create dedicated chat rooms for each task board

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (file-based)
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

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get a specific user

### Task Boards
- `GET /taskboards` - Get all task boards
- `POST /taskboards` - Create a new task board
- `GET /taskboards/{id}` - Get a specific task board
- `PUT /taskboards/{id}` - Update a task board
- `DELETE /taskboards/{id}` - Delete a task board

### Tasks
- `GET /tasks` - Get all tasks (supports filtering by status, board_id, assigned_user_id)
- `POST /tasks` - Create a new task
- `GET /tasks/{id}` - Get a specific task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

### Messages
- `GET /messages` - Get all messages (supports filtering by board_id, user_id)
- `POST /messages` - Create a new message
- `GET /messages/{id}` - Get a specific message
- `DELETE /messages/{id}` - Delete a message

### Chat Rooms
- `GET /chatrooms` - Get all chat rooms (supports filtering by board_id)
- `POST /chatrooms` - Create a new chat room
- `GET /chatrooms/{id}` - Get a specific chat room
- `DELETE /chatrooms/{id}` - Delete a chat room

### Health Check
- `GET /health` - Check API health status

## Database Schema

### Users
- `user_id` (Primary Key)
- `name`
- `email` (Unique)

### TaskBoards
- `board_id` (Primary Key)
- `title`
- `user_id` (Foreign Key to Users)
- `created_at`

### Tasks
- `task_id` (Primary Key)
- `title`
- `description`
- `status` (default: "todo")
- `due_date`
- `assigned_user_id` (Foreign Key to Users)
- `board_id` (Foreign Key to TaskBoards)
- `created_at`
- `updated_at`

### Messages
- `message_id` (Primary Key)
- `content`
- `timestamp`
- `user_id` (Foreign Key to Users)
- `board_id` (Foreign Key to TaskBoards)

### ChatRooms
- `room_id` (Primary Key)
- `name`
- `board_id` (Foreign Key to TaskBoards)
- `created_at`

## Example Usage

### Create a User

### Create a Task Board

### Create a Task

### Update Task Status (Drag-and-Drop Simulation)

### Send a Chat Message

## Deployment

### Render.com Deployment

1. Push your code to a Git repository (GitHub, GitLab, etc.)

2. Create a new Web Service on Render.com

3. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. The application will automatically use the PORT environment variable provided by Render

## Environment Variables

- `PORT` - Server port (default: 8000)

## Development

To run in development mode with auto-reload:

## Production Considerations

For production deployment, consider:
- Adding authentication and authorization
- Implementing rate limiting
- Adding request validation and error handling
- Setting up proper logging
- Using PostgreSQL instead of SQLite for better concurrency
- Implementing WebSocket support for real-time features
- Adding data backup strategies
- Implementing proper CORS policies

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.