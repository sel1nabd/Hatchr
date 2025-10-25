import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr

# Database setup
DATABASE_URL = "sqlite:///./supboys.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    events = relationship("Event", back_populates="creator", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    
    user = relationship("User", back_populates="profile")
    interests = relationship("Interest", back_populates="profile", cascade="all, delete-orphan")


class Interest(Base):
    __tablename__ = "interests"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    interest_name = Column(String(100), nullable=False)
    
    profile = relationship("Profile", back_populates="interests")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("User", back_populates="events")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class InterestBase(BaseModel):
    interest_name: str


class InterestCreate(InterestBase):
    pass


class InterestResponse(InterestBase):
    id: int
    profile_id: int
    
    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = None


class ProfileCreate(ProfileBase):
    interests: Optional[List[str]] = []


class ProfileUpdate(ProfileBase):
    interests: Optional[List[str]] = None


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    interests: List[InterestResponse] = []
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    profile: Optional[ProfileCreate] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile: Optional[ProfileUpdate] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    profile: Optional[ProfileResponse] = None
    
    class Config:
        from_attributes = True


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    date: datetime


class EventCreate(EventBase):
    created_by: int


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[datetime] = None


class EventResponse(EventBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    sender_id: int
    receiver_id: int


class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    sent_at: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="Sup Boys API",
    description="A social platform for fostering friendships and group activities",
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
        "message": "Welcome to Sup Boys API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# User endpoints
@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with their profiles and interests"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with optional profile and interests"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.flush()
    
    # Create profile if provided
    if user.profile:
        db_profile = Profile(
            user_id=db_user.id,
            bio=user.profile.bio,
            location=user.profile.location
        )
        db.add(db_profile)
        db.flush()
        
        # Add interests if provided
        if user.profile.interests:
            for interest_name in user.profile.interests:
                db_interest = Interest(
                    profile_id=db_profile.id,
                    interest_name=interest_name
                )
                db.add(db_interest)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update a user's information"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.email is not None:
        # Check if new email is already taken by another user
        existing = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        db_user.email = user_update.email
    
    # Update profile if provided
    if user_update.profile is not None:
        db_profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        
        if not db_profile:
            # Create profile if it doesn't exist
            db_profile = Profile(user_id=user_id)
            db.add(db_profile)
            db.flush()
        
        if user_update.profile.bio is not None:
            db_profile.bio = user_update.profile.bio
        if user_update.profile.location is not None:
            db_profile.location = user_update.profile.location
        
        # Update interests if provided
        if user_update.profile.interests is not None:
            # Delete existing interests
            db.query(Interest).filter(Interest.profile_id == db_profile.id).delete()
            
            # Add new interests
            for interest_name in user_update.profile.interests:
                db_interest = Interest(
                    profile_id=db_profile.id,
                    interest_name=interest_name
                )
                db.add(db_interest)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None


# Event endpoints
@app.get("/events", response_model=List[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all events with optional location filter"""
    query = db.query(Event)
    
    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))
    
    events = query.order_by(Event.date).offset(skip).limit(limit).all()
    return events


@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    # Verify creator exists
    creator = db.query(User).filter(User.id == event.created_by).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator user not found")
    
    db_event = Event(
        name=event.name,
        description=event.description,
        location=event.location,
        date=event.date,
        created_by=event.created_by
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    """Update an event"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event_update.name is not None:
        db_event.name = event_update.name
    if event_update.description is not None:
        db_event.description = event_update.description
    if event_update.location is not None:
        db_event.location = event_update.location
    if event_update.date is not None:
        db_event.date = event_update.date
    
    db.commit()
    db.refresh(db_event)
    return db_event


@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return None


# Message endpoints
@app.get("/messages", response_model=List[MessageResponse])
def get_messages(
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get messages, optionally filtered by user (sent or received)"""
    query = db.query(Message)
    
    if user_id:
        query = query.filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        )
    
    messages = query.order_by(Message.sent_at.desc()).offset(skip).limit(limit).all()
    return messages


@app.post("/messages", response_model=MessageResponse, status_code=201)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Send a message between users"""
    # Verify sender exists
    sender = db.query(User).filter(User.id == message.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender user not found")
    
    # Verify receiver exists
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver user not found")
    
    db_message = Message(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get("/messages/conversation/{user1_id}/{user2_id}", response_model=List[MessageResponse])
def get_conversation(
    user1_id: int,
    user2_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get conversation between two users"""
    messages = db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.sent_at).offset(skip).limit(limit).all()
    
    return messages


# Interest matching endpoint
@app.get("/users/{user_id}/matches", response_model=List[UserResponse])
def get_user_matches(user_id: int, db: Session = Depends(get_db)):
    """Find users with similar interests"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.profile:
        return []
    
    # Get user's interests
    user_interests = [i.interest_name for i in user.profile.interests]
    
    if not user_interests:
        return []
    
    # Find other users with matching interests
    matches = db.query(User).join(Profile).join(Interest).filter(
        Interest.interest_name.in_(user_interests),
        User.id != user_id
    ).distinct().limit(20).all()
    
    return matches


# Profile endpoints
@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a specific profile by ID"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)