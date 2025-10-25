import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./teamtask_pro.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    taskboards = relationship("TaskBoard", back_populates="owner")
    tasks = relationship("Task", back_populates="assigned_user")
    messages = relationship("Message", back_populates="user")

class TaskBoard(Base):
    __tablename__ = "taskboards"
    board_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="taskboards")
    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="board", cascade="all, delete-orphan")
    chatrooms = relationship("ChatRoom", back_populates="board", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="todo")
    due_date = Column(DateTime, nullable=True)
    assigned_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    board_id = Column(Integer, ForeignKey("taskboards.board_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assigned_user = relationship("User", back_populates="tasks")
    board = relationship("TaskBoard", back_populates="tasks")

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    board_id = Column(Integer, ForeignKey("taskboards.board_id"), nullable=False)
    
    user = relationship("User", back_populates="messages")
    board = relationship("TaskBoard", back_populates="messages")

class ChatRoom(Base):
    __tablename__ = "chatrooms"
    room_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    board_id = Column(Integer, ForeignKey("taskboards.board_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    board = relationship("TaskBoard", back_populates="chatrooms")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int
    
    class Config:
        from_attributes = True

class TaskBoardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    user_id: int

class TaskBoardCreate(TaskBoardBase):
    pass

class TaskBoardUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    user_id: Optional[int] = None

class TaskBoardResponse(TaskBoardBase):
    board_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="todo")
    due_date: Optional[datetime] = None
    assigned_user_id: Optional[int] = None
    board_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_user_id: Optional[int] = None
    board_id: Optional[int] = None

class TaskResponse(TaskBase):
    task_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    user_id: int
    board_id: int

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    message_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatRoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    board_id: int

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoomResponse(ChatRoomBase):
    room_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(
    title="TeamTask Pro API",
    description="A task management application for remote teams with real-time collaboration",
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
        "message": "Welcome to TeamTask Pro API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# TaskBoard endpoints
@app.get("/taskboards", response_model=List[TaskBoardResponse])
def get_taskboards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    taskboards = db.query(TaskBoard).offset(skip).limit(limit).all()
    return taskboards

@app.post("/taskboards", response_model=TaskBoardResponse, status_code=201)
def create_taskboard(taskboard: TaskBoardCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == taskboard.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_taskboard = TaskBoard(title=taskboard.title, user_id=taskboard.user_id)
    db.add(new_taskboard)
    db.commit()
    db.refresh(new_taskboard)
    return new_taskboard

@app.get("/taskboards/{board_id}", response_model=TaskBoardResponse)
def get_taskboard(board_id: int, db: Session = Depends(get_db)):
    taskboard = db.query(TaskBoard).filter(TaskBoard.board_id == board_id).first()
    if not taskboard:
        raise HTTPException(status_code=404, detail="TaskBoard not found")
    return taskboard

@app.put("/taskboards/{board_id}", response_model=TaskBoardResponse)
def update_taskboard(board_id: int, taskboard_update: TaskBoardUpdate, db: Session = Depends(get_db)):
    taskboard = db.query(TaskBoard).filter(TaskBoard.board_id == board_id).first()
    if not taskboard:
        raise HTTPException(status_code=404, detail="TaskBoard not found")
    
    if taskboard_update.title is not None:
        taskboard.title = taskboard_update.title
    
    if taskboard_update.user_id is not None:
        user = db.query(User).filter(User.user_id == taskboard_update.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        taskboard.user_id = taskboard_update.user_id
    
    db.commit()
    db.refresh(taskboard)
    return taskboard

@app.delete("/taskboards/{board_id}", status_code=204)
def delete_taskboard(board_id: int, db: Session = Depends(get_db)):
    taskboard = db.query(TaskBoard).filter(TaskBoard.board_id == board_id).first()
    if not taskboard:
        raise HTTPException(status_code=404, detail="TaskBoard not found")
    
    db.delete(taskboard)
    db.commit()
    return None

# Task endpoints
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    board_id: Optional[int] = None,
    assigned_user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if board_id:
        query = query.filter(Task.board_id == board_id)
    if assigned_user_id:
        query = query.filter(Task.assigned_user_id == assigned_user_id)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if task.assigned_user_id:
        user = db.query(User).filter(User.user_id == task.assigned_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")
    
    if task.board_id:
        board = db.query(TaskBoard).filter(TaskBoard.board_id == task.board_id).first()
        if not board:
            raise HTTPException(status_code=404, detail="TaskBoard not found")
    
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date,
        assigned_user_id=task.assigned_user_id,
        board_id=task.board_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.assigned_user_id is not None:
        user = db.query(User).filter(User.user_id == task_update.assigned_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Assigned user not found")
        task.assigned_user_id = task_update.assigned_user_id
    if task_update.board_id is not None:
        board = db.query(TaskBoard).filter(TaskBoard.board_id == task_update.board_id).first()
        if not board:
            raise HTTPException(status_code=404, detail="TaskBoard not found")
        task.board_id = task_update.board_id
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return None

# Message endpoints
@app.get("/messages", response_model=List[MessageResponse])
def get_messages(
    skip: int = 0,
    limit: int = 100,
    board_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Message)
    
    if board_id:
        query = query.filter(Message.board_id == board_id)
    if user_id:
        query = query.filter(Message.user_id == user_id)
    
    messages = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    return messages

@app.post("/messages", response_model=MessageResponse, status_code=201)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    board = db.query(TaskBoard).filter(TaskBoard.board_id == message.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="TaskBoard not found")
    
    new_message = Message(
        content=message.content,
        user_id=message.user_id,
        board_id=message.board_id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@app.get("/messages/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.message_id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@app.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.message_id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    return None

# ChatRoom endpoints
@app.get("/chatrooms", response_model=List[ChatRoomResponse])
def get_chatrooms(
    skip: int = 0,
    limit: int = 100,
    board_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ChatRoom)
    
    if board_id:
        query = query.filter(ChatRoom.board_id == board_id)
    
    chatrooms = query.offset(skip).limit(limit).all()
    return chatrooms

@app.post("/chatrooms", response_model=ChatRoomResponse, status_code=201)
def create_chatroom(chatroom: ChatRoomCreate, db: Session = Depends(get_db)):
    board = db.query(TaskBoard).filter(TaskBoard.board_id == chatroom.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="TaskBoard not found")
    
    new_chatroom = ChatRoom(name=chatroom.name, board_id=chatroom.board_id)
    db.add(new_chatroom)
    db.commit()
    db.refresh(new_chatroom)
    return new_chatroom

@app.get("/chatrooms/{room_id}", response_model=ChatRoomResponse)
def get_chatroom(room_id: int, db: Session = Depends(get_db)):
    chatroom = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="ChatRoom not found")
    return chatroom

@app.delete("/chatrooms/{room_id}", status_code=204)
def delete_chatroom(room_id: int, db: Session = Depends(get_db)):
    chatroom = db.query(ChatRoom).filter(ChatRoom.room_id == room_id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="ChatRoom not found")
    
    db.delete(chatroom)
    db.commit()
    return None

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)