import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Database setup
DATABASE_URL = "sqlite:///./supboys.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    profile_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("MessageModel", back_populates="user")


class CommunityModel(Base):
    __tablename__ = "communities"
    
    community_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("MessageModel", back_populates="community")
    threads = relationship("ThreadModel", back_populates="community")
    events = relationship("EventModel", back_populates="community")


class MessageModel(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    community_id = Column(Integer, ForeignKey("communities.community_id"), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserModel", back_populates="messages")
    community = relationship("CommunityModel", back_populates="messages")


class ThreadModel(Base):
    __tablename__ = "threads"
    
    thread_id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.community_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    community = relationship("CommunityModel", back_populates="threads")


class EventModel(Base):
    __tablename__ = "events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.community_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    date_time = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    community = relationship("CommunityModel", back_populates="events")


# Pydantic Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    profile_info: Optional[str] = None


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    profile_info: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class CommunityResponse(BaseModel):
    community_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    user_id: int
    content: str = Field(..., min_length=1)
    media_url: Optional[str] = None


class MessageResponse(BaseModel):
    message_id: int
    user_id: int
    community_id: int
    content: str
    media_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ThreadCreate(BaseModel):
    community_id: int
    user_id: int
    title: str = Field(..., min_length=3, max_length=200)
    content: Optional[str] = None


class ThreadResponse(BaseModel):
    thread_id: int
    community_id: int
    user_id: int
    title: str
    content: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    community_id: int
    user_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    date_time: datetime
    location: Optional[str] = None


class EventResponse(BaseModel):
    event_id: int
    community_id: int
    user_id: int
    title: str
    description: Optional[str]
    date_time: datetime
    location: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed initial data if database is empty
    db = SessionLocal()
    try:
        if db.query(UserModel).count() == 0:
            # Create sample users
            sample_users = [
                UserModel(username="john_doe", email="john@example.com", profile_info="Tech enthusiast"),
                UserModel(username="jane_smith", email="jane@example.com", profile_info="Community builder"),
                UserModel(username="mike_wilson", email="mike@example.com", profile_info="Event organizer"),
            ]
            db.add_all(sample_users)
            db.commit()
            
            # Create sample communities
            sample_communities = [
                CommunityModel(name="Tech Talk", description="Discuss the latest in technology"),
                CommunityModel(name="Gaming Squad", description="Connect with fellow gamers"),
                CommunityModel(name="Fitness Crew", description="Share fitness tips and motivation"),
            ]
            db.add_all(sample_communities)
            db.commit()
            
            # Create sample messages
            sample_messages = [
                MessageModel(user_id=1, community_id=1, content="Welcome to Tech Talk!"),
                MessageModel(user_id=2, community_id=2, content="Who's up for a gaming session?"),
            ]
            db.add_all(sample_messages)
            db.commit()
            
            # Create sample threads
            sample_threads = [
                ThreadModel(community_id=1, user_id=1, title="Best programming languages in 2024", content="What are your thoughts?"),
                ThreadModel(community_id=2, user_id=2, title="Favorite games of all time", content="Share your top picks!"),
            ]
            db.add_all(sample_threads)
            db.commit()
            
            # Create sample events
            sample_events = [
                EventModel(
                    community_id=1, 
                    user_id=3, 
                    title="Tech Meetup", 
                    description="Monthly tech networking event",
                    date_time=datetime(2024, 12, 15, 18, 0),
                    location="Downtown Convention Center"
                ),
                EventModel(
                    community_id=3, 
                    user_id=3, 
                    title="Morning Yoga Session", 
                    description="Start your day with yoga",
                    date_time=datetime(2024, 12, 10, 7, 0),
                    location="Central Park"
                ),
            ]
            db.add_all(sample_events)
            db.commit()
    finally:
        db.close()
    
    yield
    
    # Shutdown: cleanup if needed


# FastAPI app
app = FastAPI(
    title="Sup Boys API",
    description="A community-driven social platform for connecting and engaging",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to Sup Boys API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# User endpoints
@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def get_users(skip: int = 0, limit: int = 100):
    """Get all users"""
    db = next(get_db())
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int):
    """Get a specific user by ID"""
    db = next(get_db())
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate):
    """Create a new user"""
    db = next(get_db())
    
    # Check if username or email already exists
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Community endpoints
@app.get("/communities", response_model=List[CommunityResponse], tags=["Communities"])
def get_communities(skip: int = 0, limit: int = 100):
    """Get all communities"""
    db = next(get_db())
    communities = db.query(CommunityModel).offset(skip).limit(limit).all()
    return communities


@app.get("/communities/{community_id}", response_model=CommunityResponse, tags=["Communities"])
def get_community(community_id: int):
    """Get a specific community by ID"""
    db = next(get_db())
    community = db.query(CommunityModel).filter(CommunityModel.community_id == community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return community


@app.post("/communities", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED, tags=["Communities"])
def create_community(community: CommunityCreate):
    """Create a new community"""
    db = next(get_db())
    db_community = CommunityModel(**community.model_dump())
    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return db_community


# Message endpoints
@app.get("/communities/{community_id}/messages", response_model=List[MessageResponse], tags=["Messages"])
def get_community_messages(community_id: int, skip: int = 0, limit: int = 100):
    """Get all messages in a community"""
    db = next(get_db())
    
    # Verify community exists
    community = db.query(CommunityModel).filter(CommunityModel.community_id == community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    messages = db.query(MessageModel).filter(
        MessageModel.community_id == community_id
    ).order_by(MessageModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return messages


@app.post("/communities/{community_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Messages"])
def create_message(community_id: int, message: MessageCreate):
    """Create a new message in a community"""
    db = next(get_db())
    
    # Verify community exists
    community = db.query(CommunityModel).filter(CommunityModel.community_id == community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.user_id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_message = MessageModel(
        community_id=community_id,
        **message.model_dump()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


# Thread endpoints
@app.get("/threads", response_model=List[ThreadResponse], tags=["Threads"])
def get_threads(community_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    """Get all threads, optionally filtered by community"""
    db = next(get_db())
    query = db.query(ThreadModel)
    
    if community_id:
        query = query.filter(ThreadModel.community_id == community_id)
    
    threads = query.order_by(ThreadModel.created_at.desc()).offset(skip).limit(limit).all()
    return threads


@app.get("/threads/{thread_id}", response_model=ThreadResponse, tags=["Threads"])
def get_thread(thread_id: int):
    """Get a specific thread by ID"""
    db = next(get_db())
    thread = db.query(ThreadModel).filter(ThreadModel.thread_id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@app.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED, tags=["Threads"])
def create_thread(thread: ThreadCreate):
    """Create a new discussion thread"""
    db = next(get_db())
    
    # Verify community exists
    community = db.query(CommunityModel).filter(CommunityModel.community_id == thread.community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.user_id == thread.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_thread = ThreadModel(**thread.model_dump())
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread


# Event endpoints
@app.get("/events", response_model=List[EventResponse], tags=["Events"])
def get_events(community_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    """Get all events, optionally filtered by community"""
    db = next(get_db())
    query = db.query(EventModel)
    
    if community_id:
        query = query.filter(EventModel.community_id == community_id)
    
    events = query.order_by(EventModel.date_time.asc()).offset(skip).limit(limit).all()
    return events


@app.get("/events/{event_id}", response_model=EventResponse, tags=["Events"])
def get_event(event_id: int):
    """Get a specific event by ID"""
    db = next(get_db())
    event = db.query(EventModel).filter(EventModel.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED, tags=["Events"])
def create_event(event: EventCreate):
    """Create a new event"""
    db = next(get_db())
    
    # Verify community exists
    community = db.query(CommunityModel).filter(CommunityModel.community_id == event.community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.user_id == event.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_event = EventModel(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)