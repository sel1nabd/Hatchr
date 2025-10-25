import os
from datetime import date
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field

# Database setup
DATABASE_URL = "sqlite:///./tasktrack.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    completed = Column(Boolean, default=False)


# Pydantic Models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    due_date: Optional[date] = Field(None, description="Due date for the task")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    due_date: Optional[date] = Field(None, description="Due date for the task")
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    completed: bool

    class Config:
        from_attributes = True


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed
    pass


# FastAPI app
app = FastAPI(
    title="TaskTrack API",
    description="A simple todo list app for personal task management",
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


# API Endpoints
@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to TaskTrack API",
        "docs": "/docs",
        "endpoints": {
            "list_tasks": "GET /tasks",
            "create_task": "POST /tasks",
            "get_task": "GET /tasks/{id}",
            "update_task": "PUT /tasks/{id}",
            "delete_task": "DELETE /tasks/{id}",
            "complete_task": "PATCH /tasks/{id}/complete"
        }
    }


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def list_tasks(
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all tasks with optional filtering by completion status
    
    - **completed**: Filter by completion status (optional)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    query = db.query(TaskDB)
    
    if completed is not None:
        query = query.filter(TaskDB.completed == completed)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task
    
    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **due_date**: Due date in YYYY-MM-DD format (optional)
    """
    db_task = TaskDB(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        completed=False
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID
    
    - **task_id**: The ID of the task to retrieve
    """
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task
    
    - **task_id**: The ID of the task to update
    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **due_date**: New due date (optional)
    - **completed**: New completion status (optional)
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task
    
    - **task_id**: The ID of the task to delete
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    
    db.delete(db_task)
    db.commit()
    return None


@app.patch("/tasks/{task_id}/complete", response_model=TaskResponse, tags=["Tasks"])
def mark_task_complete(task_id: int, db: Session = Depends(get_db)):
    """
    Mark a task as complete
    
    - **task_id**: The ID of the task to mark as complete
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    
    db_task.completed = True
    db.commit()
    db.refresh(db_task)
    return db_task


@app.patch("/tasks/{task_id}/incomplete", response_model=TaskResponse, tags=["Tasks"])
def mark_task_incomplete(task_id: int, db: Session = Depends(get_db)):
    """
    Mark a task as incomplete
    
    - **task_id**: The ID of the task to mark as incomplete
    """
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    
    db_task.completed = False
    db.commit()
    db.refresh(db_task)
    return db_task


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "TaskTrack API"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)