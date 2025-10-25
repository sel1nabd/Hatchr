import os
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./financesync.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ClientModel(Base):
    __tablename__ = "clients"
    
    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))
    address = Column(Text)
    date_of_birth = Column(Date)
    occupation = Column(String(255))
    risk_profile = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    financial_data = relationship("FinancialDataModel", back_populates="client", cascade="all, delete-orphan")
    tasks = relationship("TaskModel", back_populates="client", cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="client", cascade="all, delete-orphan")


class FinancialDataModel(Base):
    __tablename__ = "financial_data"
    
    data_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    portfolio_value = Column(Float, nullable=False)
    annual_income = Column(Float)
    net_worth = Column(Float)
    investment_goals = Column(Text)
    asset_allocation = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("ClientModel", back_populates="financial_data")


class TaskModel(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), default="pending")
    priority = Column(String(50), default="medium")
    assigned_to = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    client = relationship("ClientModel", back_populates="tasks")


class ReportModel(Base):
    __tablename__ = "reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    report_type = Column(String(100), nullable=False)
    report_name = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    period_start = Column(Date)
    period_end = Column(Date)
    
    client = relationship("ClientModel", back_populates="reports")


class DocumentModel(Base):
    __tablename__ = "documents"
    
    document_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    description = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("ClientModel", back_populates="documents")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = None
    risk_profile: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = None
    risk_profile: Optional[str] = None


class Client(ClientBase):
    client_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FinancialDataBase(BaseModel):
    client_id: int
    portfolio_value: float = Field(..., ge=0)
    annual_income: Optional[float] = Field(None, ge=0)
    net_worth: Optional[float] = None
    investment_goals: Optional[str] = None
    asset_allocation: Optional[str] = None


class FinancialDataCreate(FinancialDataBase):
    pass


class FinancialData(FinancialDataBase):
    data_id: int
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    client_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: date
    status: Optional[str] = Field(default="pending", pattern="^(pending|in_progress|completed|cancelled)$")
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    assigned_to: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    task_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    client_id: int
    report_type: str = Field(..., min_length=1, max_length=100)
    report_name: str = Field(..., min_length=1, max_length=255)
    data: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class ReportCreate(ReportBase):
    pass


class Report(ReportBase):
    report_id: int
    generated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    client_id: int
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_type: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    document_id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="FinanceSync",
    description="A streamlined CRM tailored for financial professionals",
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
        "message": "Welcome to FinanceSync API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "clients": "/clients",
            "financial_data": "/financial-data",
            "tasks": "/tasks",
            "reports": "/reports",
            "documents": "/documents"
        }
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
def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    """Update a client's information"""
    db_client = db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if email is being updated and if it's already taken
    if client_update.email and client_update.email != db_client.email:
        existing_client = db.query(ClientModel).filter(ClientModel.email == client_update.email).first()
        if existing_client:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db_client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_client)
    return db_client


@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client"""
    db_client = db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None


# Financial Data endpoints
@app.get("/financial-data", response_model=List[FinancialData])
def get_financial_data(client_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve financial data, optionally filtered by client_id"""
    query = db.query(FinancialDataModel)
    if client_id:
        query = query.filter(FinancialDataModel.client_id == client_id)
    financial_data = query.offset(skip).limit(limit).all()
    return financial_data


@app.post("/financial-data", response_model=FinancialData, status_code=201)
def create_financial_data(financial_data: FinancialDataCreate, db: Session = Depends(get_db)):
    """Create new financial data entry for a client"""
    # Verify client exists
    client = db.query(ClientModel).filter(ClientModel.client_id == financial_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_financial_data = FinancialDataModel(**financial_data.model_dump())
    db.add(db_financial_data)
    db.commit()
    db.refresh(db_financial_data)
    return db_financial_data


@app.get("/financial-data/{data_id}", response_model=FinancialData)
def get_financial_data_by_id(data_id: int, db: Session = Depends(get_db)):
    """Retrieve specific financial data by ID"""
    financial_data = db.query(FinancialDataModel).filter(FinancialDataModel.data_id == data_id).first()
    if not financial_data:
        raise HTTPException(status_code=404, detail="Financial data not found")
    return financial_data


# Task endpoints
@app.get("/tasks", response_model=List[Task])
def get_tasks(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve tasks, optionally filtered by client_id and status"""
    query = db.query(TaskModel)
    if client_id:
        query = query.filter(TaskModel.client_id == client_id)
    if status:
        query = query.filter(TaskModel.status == status)
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
def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump()
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    # Set completed_at if status is completed
    if task_update.status == "completed" and not db_task.completed_at:
        db_task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_task)
    return db_task


# Report endpoints
@app.get("/reports", response_model=List[Report])
def get_reports(
    client_id: Optional[int] = None,
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve reports, optionally filtered by client_id and report_type"""
    query = db.query(ReportModel)
    if client_id:
        query = query.filter(ReportModel.client_id == client_id)
    if report_type:
        query = query.filter(ReportModel.report_type == report_type)
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


# Document endpoints
@app.get("/documents", response_model=List[Document])
def get_documents(
    client_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve documents, optionally filtered by client_id"""
    query = db.query(DocumentModel)
    if client_id:
        query = query.filter(DocumentModel.client_id == client_id)
    documents = query.offset(skip).limit(limit).all()
    return documents


@app.post("/documents", response_model=Document, status_code=201)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """Create a new document entry for a client"""
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
    """Delete a document"""
    db_document = db.query(DocumentModel).filter(DocumentModel.document_id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_document)
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