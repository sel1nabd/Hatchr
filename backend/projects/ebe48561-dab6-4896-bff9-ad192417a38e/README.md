# TaskTrack

A simple todo list app for personal task management built with FastAPI and SQLite.

## Features

- ✅ Create tasks with title, description, and due date
- ✅ Edit existing tasks
- ✅ Delete tasks
- ✅ List all tasks with optional filtering
- ✅ Mark tasks as complete or incomplete
- ✅ RESTful API design
- ✅ Auto-generated API documentation
- ✅ SQLite database (no external dependencies)

## Setup

### Local Development

1. **Install dependencies:**

2. **Run the server:**
   
   Or using Python directly:

3. **Visit API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Environment Variables

- `PORT`: Server port (default: 8000)

Example:

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks (supports filtering by completion status) |
| POST | `/tasks` | Create a new task |
| GET | `/tasks/{id}` | Get a specific task by ID |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| PATCH | `/tasks/{id}/complete` | Mark a task as complete |
| PATCH | `/tasks/{id}/incomplete` | Mark a task as incomplete |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API information |
| GET | `/health` | Health check endpoint |

## API Usage Examples

### Create a Task


### List All Tasks


### List Completed Tasks Only


### Get a Specific Task


### Update a Task


### Mark Task as Complete


### Delete a Task


## Database Schema

### Tasks Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique task identifier |
| title | STRING | NOT NULL | Task title |
| description | STRING | NULLABLE | Task description |
| due_date | DATE | NULLABLE | Task due date |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

The application will automatically use the `PORT` environment variable provided by Render.

### Other Platforms

The application is compatible with any platform that supports Python web applications:
- Heroku
- Railway
- Fly.io
- Google Cloud Run
- AWS Elastic Beanstalk

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight, file-based database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server implementation

## Project Structure


## Development

### Running Tests

The application includes comprehensive error handling and validation:
- 404 errors for non-existent tasks
- Input validation for all fields
- Proper HTTP status codes

### CORS

CORS is enabled for all origins, making it easy to integrate with any frontend application.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please refer to the API documentation at `/docs` when running the application.