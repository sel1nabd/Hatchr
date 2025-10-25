# Markdown Notes

A minimalistic note-taking app with markdown support, focusing on simplicity and essential features.

## Features

- ✨ **Markdown Support**: Write notes in markdown format
- 🏷️ **Tagging System**: Organize notes with tags (many-to-many relationship)
- 🔍 **Search Functionality**: Search notes by title or content
- 📝 **CRUD Operations**: Full create, read, update, delete for notes and tags
- 🚀 **Fast & Lightweight**: Built with FastAPI and SQLite
- 📚 **Auto-generated Documentation**: Interactive API docs at `/docs`

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Setup

### Local Development

1. **Clone the repository**

2. **Install dependencies**

3. **Run the server**

4. **Access the application**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Production Deployment (Render.com)

1. **Create a new Web Service** on Render.com
2. **Connect your repository**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Deploy**

The app automatically uses the `PORT` environment variable provided by Render.

## API Endpoints

### Notes

- `GET /notes` - Get all notes (supports search and tag filtering)
  - Query params: `search`, `tag`, `skip`, `limit`
- `POST /notes` - Create a new note
- `GET /notes/{id}` - Get a specific note
- `PUT /notes/{id}` - Update a note
- `DELETE /notes/{id}` - Delete a note

### Tags

- `GET /tags` - Get all tags
- `POST /tags` - Create a new tag
- `GET /tags/{id}` - Get a specific tag
- `PUT /tags/{id}` - Update a tag
- `DELETE /tags/{id}` - Delete a tag

### Search

- `GET /search?q={query}` - Search notes by title or content

## API Usage Examples

### Create a Note


### Get All Notes


### Search Notes


### Filter by Tag


### Create a Tag


### Update a Note


### Delete a Note


## Database Schema

### Notes Table
- `id` (Integer, Primary Key)
- `title` (String, Required)
- `content` (Text, Default: "")
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Tags Table
- `id` (Integer, Primary Key)
- `name` (String, Unique, Required)

### NoteTags Table (Junction Table)
- `id` (Integer, Primary Key)
- `note_id` (Foreign Key → Notes)
- `tag_id` (Foreign Key → Tags)

## Request/Response Examples

### Create Note Request

### Note Response

## Features Comparison

Unlike feature-heavy competitors (Notion, Evernote, Bear), Markdown Notes focuses on:

- ✅ Core markdown editing
- ✅ Simple tagging system
- ✅ Fast search
- ✅ Lightweight and fast
- ❌ No authentication (can be added later)
- ❌ No rich media embeds
- ❌ No collaboration features
- ❌ No mobile apps (API-first design allows future development)

## Development

### Project Structure

### Running Tests

The interactive API documentation at `/docs` provides a built-in testing interface.

### Environment Variables

- `PORT` - Server port (default: 8000)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the repository.