import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./supboys.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    bio = Column(Text, nullable=True)
    
    posts = relationship("PostDB", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan")
    events = relationship("EventDB", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("MessageDB", foreign_keys="MessageDB.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("MessageDB", foreign_keys="MessageDB.receiver_id", back_populates="receiver", cascade="all, delete-orphan")


class PostDB(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("UserDB", back_populates="posts")
    comments = relationship("CommentDB", back_populates="post", cascade="all, delete-orphan")


class CommentDB(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    post = relationship("PostDB", back_populates="comments")
    user = relationship("UserDB", back_populates="comments")


class EventDB(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    
    user = relationship("UserDB", back_populates="events")


class MessageDB(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    sender = relationship("UserDB", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("UserDB", foreign_keys=[receiver_id], back_populates="received_messages")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    
    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    user_id: int
    content: str = Field(..., min_length=1)


class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    post_id: int
    user_id: int
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    user_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")


class EventResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    date: str
    time: str
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="Sup Boys Network",
    description="A social networking platform for young men to connect based on shared interests",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Sup Boys Network API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# User endpoints
@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = db.query(UserDB).offset(skip).limit(limit).all()
    return users


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    existing_email = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = UserDB(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Check username uniqueness if updating
    if "username" in update_data:
        existing = db.query(UserDB).filter(
            UserDB.username == update_data["username"],
            UserDB.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check email uniqueness if updating
    if "email" in update_data:
        existing = db.query(UserDB).filter(
            UserDB.email == update_data["email"],
            UserDB.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None


# Post endpoints
@app.get("/posts", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 100, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all posts with optional filtering by user_id"""
    query = db.query(PostDB)
    
    if user_id:
        query = query.filter(PostDB.user_id == user_id)
    
    posts = query.order_by(PostDB.timestamp.desc()).offset(skip).limit(limit).all()
    return posts


@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    # Verify user exists
    user = db.query(UserDB).filter(UserDB.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_post = PostDB(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post"""
    db_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(db_post)
    db.commit()
    return None


# Comment endpoints
@app.get("/comments", response_model=List[CommentResponse])
def get_comments(post_id: Optional[int] = None, user_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get comments with optional filtering by post_id or user_id"""
    query = db.query(CommentDB)
    
    if post_id:
        query = query.filter(CommentDB.post_id == post_id)
    if user_id:
        query = query.filter(CommentDB.user_id == user_id)
    
    comments = query.order_by(CommentDB.timestamp.desc()).offset(skip).limit(limit).all()
    return comments


@app.post("/comments", response_model=CommentResponse, status_code=201)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """Create a new comment"""
    # Verify post exists
    post = db.query(PostDB).filter(PostDB.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Verify user exists
    user = db.query(UserDB).filter(UserDB.id == comment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_comment = CommentDB(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@app.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """Delete a comment"""
    db_comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(db_comment)
    db.commit()
    return None


# Event endpoints
@app.get("/events", response_model=List[EventResponse])
def get_events(skip: int = 0, limit: int = 100, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all events with optional filtering by user_id"""
    query = db.query(EventDB)
    
    if user_id:
        query = query.filter(EventDB.user_id == user_id)
    
    events = query.offset(skip).limit(limit).all()
    return events


@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    # Verify user exists
    user = db.query(UserDB).filter(UserDB.id == event.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_event = EventDB(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event by ID"""
    event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    db_event = db.query(EventDB).filter(EventDB.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return None


# Message endpoints
@app.get("/messages", response_model=List[MessageResponse])
def get_messages(sender_id: Optional[int] = None, receiver_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get messages with optional filtering by sender_id or receiver_id"""
    query = db.query(MessageDB)
    
    if sender_id:
        query = query.filter(MessageDB.sender_id == sender_id)
    if receiver_id:
        query = query.filter(MessageDB.receiver_id == receiver_id)
    
    messages = query.order_by(MessageDB.timestamp.desc()).offset(skip).limit(limit).all()
    return messages


@app.post("/messages", response_model=MessageResponse, status_code=201)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Create a new message"""
    # Verify sender exists
    sender = db.query(UserDB).filter(UserDB.id == message.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    # Verify receiver exists
    receiver = db.query(UserDB).filter(UserDB.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Prevent sending message to self
    if message.sender_id == message.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    db_message = MessageDB(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get("/messages/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific message by ID"""
    message = db.query(MessageDB).filter(MessageDB.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@app.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a message"""
    db_message = db.query(MessageDB).filter(MessageDB.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(db_message)
    db.commit()
    return None


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)