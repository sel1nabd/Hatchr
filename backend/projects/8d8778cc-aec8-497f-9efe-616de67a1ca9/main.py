import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field

# Database setup
DATABASE_URL = "sqlite:///./supboys.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("PostModel", back_populates="author")
    comments = relationship("CommentModel", back_populates="author")
    events = relationship("EventModel", back_populates="creator")


class GroupModel(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    member_count = Column(Integer, default=0)
    
    posts = relationship("PostModel", back_populates="group")
    events = relationship("EventModel", back_populates="group")


class EventModel(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)
    event_date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    max_attendees = Column(Integer, nullable=True)
    current_attendees = Column(Integer, default=0)
    
    creator = relationship("UserModel", back_populates="events")
    group = relationship("GroupModel", back_populates="events")


class PostModel(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    
    author = relationship("UserModel", back_populates="posts")
    group = relationship("GroupModel", back_populates="posts")
    comments = relationship("CommentModel", back_populates="post")


class CommentModel(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    
    author = relationship("UserModel", back_populates="comments")
    post = relationship("PostModel", back_populates="comments")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None
    location: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    bio: Optional[str]
    location: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=3, max_length=50)
    created_by: int


class GroupResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    created_by: int
    created_at: datetime
    member_count: int
    
    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=3, max_length=200)
    event_date: datetime
    created_by: int
    group_id: Optional[int] = None
    max_attendees: Optional[int] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    event_date: datetime
    created_by: int
    group_id: Optional[int]
    created_at: datetime
    max_attendees: Optional[int]
    current_attendees: int
    
    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    author_id: int
    group_id: Optional[int] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    group_id: Optional[int]
    created_at: datetime
    likes: int
    
    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    author_id: int
    post_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    author_id: int
    post_id: int
    created_at: datetime
    likes: int
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="SupBoys API",
    description="A social networking app for men's communities to connect and share experiences",
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
        "message": "Welcome to SupBoys API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# User endpoints
@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing_email = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Group endpoints
@app.get("/groups", response_model=List[GroupResponse])
def get_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = db.query(GroupModel).offset(skip).limit(limit).all()
    return groups


@app.get("/groups/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@app.post("/groups", response_model=GroupResponse, status_code=201)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == group.created_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if group name exists
    existing_group = db.query(GroupModel).filter(GroupModel.name == group.name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Group name already exists")
    
    db_group = GroupModel(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


# Event endpoints
@app.get("/events", response_model=List[EventResponse])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(EventModel).offset(skip).limit(limit).all()
    return events


@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == event.created_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if group exists (if group_id provided)
    if event.group_id:
        group = db.query(GroupModel).filter(GroupModel.id == event.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
    
    db_event = EventModel(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# Post endpoints
@app.get("/posts", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(PostModel).offset(skip).limit(limit).all()
    return posts


@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == post.author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if group exists (if group_id provided)
    if post.group_id:
        group = db.query(GroupModel).filter(GroupModel.id == post.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
    
    db_post = PostModel(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


# Comment endpoints
@app.get("/comments", response_model=List[CommentResponse])
def get_comments(skip: int = 0, limit: int = 100, post_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(CommentModel)
    if post_id:
        query = query.filter(CommentModel.post_id == post_id)
    comments = query.offset(skip).limit(limit).all()
    return comments


@app.get("/comments/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@app.post("/comments", response_model=CommentResponse, status_code=201)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == comment.author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if post exists
    post = db.query(PostModel).filter(PostModel.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = CommentModel(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)