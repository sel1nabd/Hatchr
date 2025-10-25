import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship
from pydantic import BaseModel, Field

# Database setup
DATABASE_URL = "sqlite:///./broconnect.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for many-to-many relationship between Users and Interests
user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('interest_id', Integer, ForeignKey('interests.id'))
)

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interests = relationship("Interest", secondary=user_interests, back_populates="users")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")


class Interest(Base):
    __tablename__ = "interests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    users = relationship("User", secondary=user_interests, back_populates="interests")


class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activities")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class InterestBase(BaseModel):
    name: str

class InterestCreate(InterestBase):
    pass

class InterestResponse(InterestBase):
    id: int
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=18, le=120)
    bio: Optional[str] = None

class UserCreate(UserBase):
    interest_ids: Optional[List[int]] = []

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    bio: Optional[str] = None
    interest_ids: Optional[List[int]] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    interests: List[InterestResponse] = []
    
    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    activity_name: str = Field(..., min_length=1, max_length=200)
    date: datetime
    location: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class ActivityCreate(ActivityBase):
    user_id: int

class ActivityResponse(ActivityBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class MessageCreate(MessageBase):
    sender_id: int
    receiver_id: int

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ConnectionBase(BaseModel):
    user1_id: int
    user2_id: int

class ConnectionCreate(ConnectionBase):
    pass

class ConnectionResponse(ConnectionBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    user_id: int
    name: str
    age: int
    bio: Optional[str]
    common_interests: List[str]
    match_score: int


# FastAPI app
app = FastAPI(
    title="Bro Connect API",
    description="A social networking app for connecting male friends through common interests and activities",
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
        "message": "Welcome to Bro Connect API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# User endpoints
@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = User(
        name=user.name,
        age=user.age,
        bio=user.bio
    )
    
    # Add interests if provided
    if user.interest_ids:
        interests = db.query(Interest).filter(Interest.id.in_(user.interest_ids)).all()
        db_user.interests = interests
    
    db.add(db_user)
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
    """Update a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.age is not None:
        db_user.age = user_update.age
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    
    # Update interests if provided
    if user_update.interest_ids is not None:
        interests = db.query(Interest).filter(Interest.id.in_(user_update.interest_ids)).all()
        db_user.interests = interests
    
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


# Interest endpoints
@app.get("/interests", response_model=List[InterestResponse])
def get_interests(db: Session = Depends(get_db)):
    """Get all interests"""
    interests = db.query(Interest).all()
    return interests


@app.post("/interests", response_model=InterestResponse, status_code=201)
def create_interest(interest: InterestCreate, db: Session = Depends(get_db)):
    """Create a new interest"""
    # Check if interest already exists
    existing = db.query(Interest).filter(Interest.name == interest.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Interest already exists")
    
    db_interest = Interest(name=interest.name)
    db.add(db_interest)
    db.commit()
    db.refresh(db_interest)
    return db_interest


# Activity endpoints
@app.get("/activities", response_model=List[ActivityResponse])
def get_activities(skip: int = 0, limit: int = 100, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all activities with optional filtering by user_id"""
    query = db.query(Activity)
    
    if user_id:
        query = query.filter(Activity.user_id == user_id)
    
    activities = query.offset(skip).limit(limit).all()
    return activities


@app.post("/activities", response_model=ActivityResponse, status_code=201)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Create a new activity"""
    # Verify user exists
    user = db.query(User).filter(User.id == activity.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_activity = Activity(
        user_id=activity.user_id,
        activity_name=activity.activity_name,
        date=activity.date,
        location=activity.location,
        description=activity.description
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@app.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get a specific activity by ID"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


# Message endpoints
@app.post("/messages", response_model=MessageResponse, status_code=201)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Send a message between users"""
    # Verify both users exist
    sender = db.query(User).filter(User.id == message.sender_id).first()
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    if message.sender_id == message.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    db_message = Message(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get("/messages", response_model=List[MessageResponse])
def get_messages(user_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get messages, optionally filtered by user_id (sent or received)"""
    query = db.query(Message)
    
    if user_id:
        query = query.filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        )
    
    messages = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    return messages


@app.get("/messages/conversation/{user1_id}/{user2_id}", response_model=List[MessageResponse])
def get_conversation(user1_id: int, user2_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get conversation between two users"""
    messages = db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.timestamp.asc()).offset(skip).limit(limit).all()
    
    return messages


# Connection endpoints
@app.get("/connections", response_model=List[ConnectionResponse])
def get_connections(user_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get connections, optionally filtered by user_id and/or status"""
    query = db.query(Connection)
    
    if user_id:
        query = query.filter(
            (Connection.user1_id == user_id) | (Connection.user2_id == user_id)
        )
    
    if status:
        query = query.filter(Connection.status == status)
    
    connections = query.all()
    return connections


@app.post("/connections", response_model=ConnectionResponse, status_code=201)
def create_connection(connection: ConnectionCreate, db: Session = Depends(get_db)):
    """Create a new connection request"""
    # Verify both users exist
    user1 = db.query(User).filter(User.id == connection.user1_id).first()
    user2 = db.query(User).filter(User.id == connection.user2_id).first()
    
    if not user1:
        raise HTTPException(status_code=404, detail="User1 not found")
    if not user2:
        raise HTTPException(status_code=404, detail="User2 not found")
    if connection.user1_id == connection.user2_id:
        raise HTTPException(status_code=400, detail="Cannot connect with yourself")
    
    # Check if connection already exists
    existing = db.query(Connection).filter(
        ((Connection.user1_id == connection.user1_id) & (Connection.user2_id == connection.user2_id)) |
        ((Connection.user1_id == connection.user2_id) & (Connection.user2_id == connection.user1_id))
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")
    
    db_connection = Connection(
        user1_id=connection.user1_id,
        user2_id=connection.user2_id,
        status="pending"
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection


@app.put("/connections/{connection_id}/status", response_model=ConnectionResponse)
def update_connection_status(connection_id: int, status: str, db: Session = Depends(get_db)):
    """Update connection status (accept/reject)"""
    if status not in ["accepted", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'accepted', 'rejected', or 'pending'")
    
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    connection.status = status
    db.commit()
    db.refresh(connection)
    return connection


# Matchmaking endpoint
@app.get("/users/{user_id}/matches", response_model=List[MatchResponse])
def get_matches(user_id: int, min_common_interests: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    """Get potential matches based on common interests"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_interest_ids = [interest.id for interest in user.interests]
    
    if not user_interest_ids:
        return []
    
    # Get all other users
    other_users = db.query(User).filter(User.id != user_id).all()
    
    matches = []
    for other_user in other_users:
        other_interest_ids = [interest.id for interest in other_user.interests]
        common_interest_ids = set(user_interest_ids) & set(other_interest_ids)
        
        if len(common_interest_ids) >= min_common_interests:
            common_interest_names = [
                interest.name for interest in other_user.interests 
                if interest.id in common_interest_ids
            ]
            
            matches.append({
                "user_id": other_user.id,
                "name": other_user.name,
                "age": other_user.age,
                "bio": other_user.bio,
                "common_interests": common_interest_names,
                "match_score": len(common_interest_ids)
            })
    
    # Sort by match score (number of common interests)
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matches[:limit]


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}


# Seed data endpoint (for development/testing)
@app.post("/seed-data", status_code=201)
def seed_data(db: Session = Depends(get_db)):
    """Seed the database with sample data"""
    # Check if data already exists
    if db.query(User).count() > 0:
        raise HTTPException(status_code=400, detail="Database already contains data")
    
    # Create interests
    interests_data = [
        "Sports", "Gaming", "Hiking", "Cooking", "Music",
        "Movies", "Reading", "Travel", "Fitness", "Technology"
    ]
    interests = []
    for interest_name in interests_data:
        interest = Interest(name=interest_name)
        db.add(interest)
        interests.append(interest)
    
    db.commit()
    
    # Create users
    users_data = [
        {"name": "John Doe", "age": 28, "bio": "Love sports and outdoor activities", "interests": [0, 2, 8]},
        {"name": "Mike Smith", "age": 32, "bio": "Tech enthusiast and gamer", "interests": [1, 9, 4]},
        {"name": "Chris Johnson", "age": 25, "bio": "Foodie and music lover", "interests": [3, 4, 5]},
        {"name": "David Brown", "age": 30, "bio": "Adventure seeker", "interests": [2, 7, 0]},
        {"name": "Tom Wilson", "age": 27, "bio": "Fitness and wellness advocate", "interests": [8, 0, 2]},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            name=user_data["name"],
            age=user_data["age"],
            bio=user_data["bio"]
        )
        user.interests = [interests[i] for i in user_data["interests"]]
        db.add(user)
        users.append(user)
    
    db.commit()
    
    # Create activities
    activities_data = [
        {
            "user_id": 1,
            "activity_name": "Basketball Game",
            "date": datetime(2024, 2, 15, 18, 0),
            "location": "Central Park Courts",
            "description": "Casual pickup game, all skill levels welcome"
        },
        {
            "user_id": 2,
            "activity_name": "Gaming Tournament",
            "date": datetime(2024, 2, 20, 19, 0),
            "location": "GameStop Downtown",
            "description": "FIFA tournament with prizes"
        },
        {
            "user_id": 3,
            "activity_name": "Cooking Class",
            "date": datetime(2024, 2, 18, 17, 0),
            "location": "Culinary Institute",
            "description": "Learn to make Italian cuisine"
        }
    ]
    
    for activity_data in activities_data:
        activity = Activity(**activity_data)
        db.add(activity)
    
    db.commit()
    
    # Create connections
    connections_data = [
        {"user1_id": 1, "user2_id": 5, "status": "accepted"},
        {"user1_id": 2, "user2_id": 3, "status": "pending"},
        {"user1_id": 1, "user2_id": 4, "status": "accepted"},
    ]
    
    for conn_data in connections_data:
        connection = Connection(**conn_data)
        db.add(connection)
    
    db.commit()
    
    # Create messages
    messages_data = [
        {
            "sender_id": 1,
            "receiver_id": 5,
            "content": "Hey! Want to join the basketball game this weekend?"
        },
        {
            "sender_id": 5,
            "receiver_id": 1,
            "content": "Sure! What time?"
        },
        {
            "sender_id": 2,
            "receiver_id": 3,
            "content": "I saw you're into music. Want to check out that new concert?"
        }
    ]
    
    for msg_data in messages_data:
        message = Message(**msg_data)
        db.add(message)
    
    db.commit()
    
    return {"message": "Database seeded successfully"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)