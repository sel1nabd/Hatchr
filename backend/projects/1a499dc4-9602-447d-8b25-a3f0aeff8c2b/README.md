# ASDF Hub

A digital content curation platform designed to organize and share ASDF-related content, similar to Flipboard, Pocket, and Feedly.

## Features

- **Content Aggregation**: Collect and organize content from various sources
- **Customizable Feeds**: Create personalized feeds with curated content
- **Bookmarking**: Save content items to your feeds for later reference
- **Tagging and Categorization**: Organize content with custom tags
- **Social Media Sharing**: Share content to Twitter, Facebook, LinkedIn, Reddit, and Email

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Setup

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:

2. Install dependencies:

3. Run the server:

4. Visit the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get a specific user

### Content Items
- `GET /content-items` - Get all content items (supports filtering by user_id and tag)
- `POST /content-items` - Create a new content item
- `GET /content-items/{id}` - Get a specific content item
- `PUT /content-items/{id}` - Update a content item
- `DELETE /content-items/{id}` - Delete a content item

### Feeds
- `GET /feeds` - Get all feeds (supports filtering by user_id)
- `POST /feeds` - Create a new feed
- `GET /feeds/{id}` - Get a specific feed
- `PUT /feeds/{id}` - Update a feed
- `DELETE /feeds/{id}` - Delete a feed

### Tags
- `GET /tags` - Get all tags
- `GET /tags/{tag_id}` - Get a specific tag

### Bookmarking
- `POST /feeds/{feed_id}/bookmark/{content_id}` - Add content to a feed
- `DELETE /feeds/{feed_id}/bookmark/{content_id}` - Remove content from a feed

### Sharing
- `POST /share` - Generate a share URL for social media platforms

## Database Schema

### Users
- `id`: Integer (Primary Key)
- `name`: String
- `email`: String (Unique)
- `created_at`: DateTime

### ContentItems
- `id`: Integer (Primary Key)
- `title`: String
- `url`: String
- `description`: String (Optional)
- `user_id`: Integer (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime

### Tags
- `id`: Integer (Primary Key)
- `name`: String (Unique)
- `created_at`: DateTime

### Feeds
- `id`: Integer (Primary Key)
- `name`: String
- `description`: String (Optional)
- `user_id`: Integer (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime

### ContentTags (Association Table)
- `content_id`: Integer (Foreign Key)
- `tag_id`: Integer (Foreign Key)

### FeedItems (Association Table)
- `feed_id`: Integer (Foreign Key)
- `content_id`: Integer (Foreign Key)

## Usage Examples

### Create a User

### Create Content Item

### Create a Feed

### Share Content

## Deployment

### Render.com

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy

The application will automatically use the PORT environment variable provided by Render.

## Environment Variables

- `PORT`: The port number for the server (default: 8000)

## Development

To run in development mode with auto-reload:

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.