import os
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./advisorconnect.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class ClientModel(Base):
    __tablename__ = "clients"
    
    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    
    accounts = relationship("AccountModel", back_populates="client", cascade="all, delete-orphan")
    tasks = relationship("TaskModel", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="client", cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="client", cascade="all, delete-orphan")


class AccountModel(Base):
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    
    client = relationship("ClientModel", back_populates="accounts")


class TaskModel(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    description = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    
    client = relationship("ClientModel", back_populates="tasks")


class DocumentModel(Base):
    __tablename__ = "documents"
    
    document_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("ClientModel", back_populates="documents")


class ReportModel(Base):
    __tablename__ = "reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    report_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("ClientModel", back_populates="reports")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=20)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class Client(ClientBase):
    client_id: int
    
    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    client_id: int
    account_type: str = Field(..., min_length=1, max_length=100)
    balance: float = Field(..., ge=0)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    account_type: Optional[str] = Field(None, min_length=1, max_length=100)
    balance: Optional[float] = Field(None, ge=0)


class Account(AccountBase):
    account_id: int
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    client_id: int
    description: str = Field(..., min_length=1, max_length=500)
    due_date: date


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    due_date: Optional[date] = None


class Task(TaskBase):
    task_id: int
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    client_id: int
    filename: str = Field(..., min_length=1, max_length=255)


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    document_id: int
    upload_date: datetime
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    client_id: int
    report_type: str = Field(..., min_length=1, max_length=100)


class ReportCreate(ReportBase):
    pass


class Report(ReportBase):
    report_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="AdvisorConnect",
    description="A streamlined CRM specifically designed for financial advisors",
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
        "message": "Welcome to AdvisorConnect API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Client endpoints
@app.get("/clients", response_model=List[Client])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all clients with pagination"""
    clients = db.query(ClientModel).offset(skip).limit(limit).all()
    return clients


@app.post("/clients", response_model=Client, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    # Check if email already exists
    existing_client = db.query(ClientModel).filter(ClientModel.email == client.email).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_client = ClientModel(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@app.get("/clients/{client_id}", response_model=Client)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific client by ID"""
    client = db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.put("/clients/{client_id}", response_model=Client)
def update_client(client_id: int, client: ClientUpdate, db: Session = Depends(get_db)):
    """Update a client's information"""
    db_client = db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if email is being changed to an existing email
    if client.email != db_client.email:
        existing_client = db.query(ClientModel).filter(ClientModel.email == client.email).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    for key, value in client.model_dump().items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client and all associated records"""
    db_client = db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None


# Account endpoints
@app.get("/accounts", response_model=List[Account])
def get_accounts(skip: int = 0, limit: int = 100, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve all accounts with optional filtering by client_id"""
    query = db.query(AccountModel)
    if client_id:
        query = query.filter(AccountModel.client_id == client_id)
    accounts = query.offset(skip).limit(limit).all()
    return accounts


@app.post("/accounts", response_model=Account, status_code=201)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account for a client"""
    # Verify client exists
    client = db.query(ClientModel).filter(ClientModel.client_id == account.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_account = AccountModel(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@app.get("/accounts/{account_id}", response_model=Account)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific account by ID"""
    account = db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: int, account: AccountUpdate, db: Session = Depends(get_db)):
    """Update an account's information"""
    db_account = db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = account.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account


@app.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete an account"""
    db_account = db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(db_account)
    db.commit()
    return None


# Task endpoints
@app.get("/tasks", response_model=List[Task])
def get_tasks(skip: int = 0, limit: int = 100, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve all tasks with optional filtering by client_id"""
    query = db.query(TaskModel)
    if client_id:
        query = query.filter(TaskModel.client_id == client_id)
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task for a client"""
    # Verify client exists
    client = db.query(ClientModel).filter(ClientModel.client_id == task.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_task = TaskModel(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific task by ID"""
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task's information"""
    db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return None


# Document endpoints
@app.get("/documents", response_model=List[Document])
def get_documents(skip: int = 0, limit: int = 100, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve all documents with optional filtering by client_id"""
    query = db.query(DocumentModel)
    if client_id:
        query = query.filter(DocumentModel.client_id == client_id)
    documents = query.offset(skip).limit(limit).all()
    return documents


@app.post("/documents", response_model=Document, status_code=201)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """Create a new document record for a client"""
    # Verify client exists
    client = db.query(ClientModel).filter(ClientModel.client_id == document.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_document = DocumentModel(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@app.get("/documents/{document_id}", response_model=Document)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific document by ID"""
    document = db.query(DocumentModel).filter(DocumentModel.document_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document record"""
    db_document = db.query(DocumentModel).filter(DocumentModel.document_id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_document)
    db.commit()
    return None


# Report endpoints
@app.get("/reports", response_model=List[Report])
def get_reports(skip: int = 0, limit: int = 100, client_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve all reports with optional filtering by client_id"""
    query = db.query(ReportModel)
    if client_id:
        query = query.filter(ReportModel.client_id == client_id)
    reports = query.offset(skip).limit(limit).all()
    return reports


@app.post("/reports", response_model=Report, status_code=201)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """Create a new report for a client"""
    # Verify client exists
    client = db.query(ClientModel).filter(ClientModel.client_id == report.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_report = ReportModel(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@app.get("/reports/{report_id}", response_model=Report)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific report by ID"""
    report = db.query(ReportModel).filter(ReportModel.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.delete("/reports/{report_id}", status_code=204)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report"""
    db_report = db.query(ReportModel).filter(ReportModel.report_id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(db_report)
    db.commit()
    return None


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)