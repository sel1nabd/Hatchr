import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field

# Database setup
DATABASE_URL = "sqlite:///./fincrm.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class CustomerModel(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_info = Column(String)
    company = Column(String)
    notes = Column(Text)
    
    transactions = relationship("TransactionModel", back_populates="customer", cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="customer", cascade="all, delete-orphan")
    tasks = relationship("TaskModel", back_populates="customer", cascade="all, delete-orphan")
    appointments = relationship("AppointmentModel", back_populates="customer", cascade="all, delete-orphan")


class TransactionModel(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text)
    
    customer = relationship("CustomerModel", back_populates="transactions")


class ReportModel(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    report_type = Column(String, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    customer = relationship("CustomerModel", back_populates="reports")


class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    task_description = Column(Text, nullable=False)
    due_date = Column(DateTime)
    status = Column(String, default="pending")
    
    customer = relationship("CustomerModel", back_populates="tasks")


class AppointmentModel(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    location = Column(String)
    notes = Column(Text)
    
    customer = relationship("CustomerModel", back_populates="appointments")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact_info: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class Customer(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    customer_id: int
    date: datetime
    amount: float
    type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    customer_id: Optional[int] = None
    date: Optional[datetime] = None
    amount: Optional[float] = None
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class Transaction(TransactionBase):
    id: int
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    customer_id: int
    report_type: str
    content: Optional[str] = None


class Report(ReportBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    customer_id: int
    task_description: str
    due_date: Optional[datetime] = None
    status: Optional[str] = "pending"


class Task(TaskBase):
    id: int
    
    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    customer_id: int
    date_time: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


class Appointment(AppointmentBase):
    id: int
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="FinCRM API",
    description="A financial CRM tool for managing customer relationships and financial interactions",
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
        "message": "Welcome to FinCRM API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Customer Endpoints
@app.get("/customers", response_model=List[Customer])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers with pagination"""
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return customers


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    db_customer = CustomerModel(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.get("/customers/{id}", response_model=Customer)
def get_customer(id: int, db: Session = Depends(get_db)):
    """Get a specific customer by ID"""
    customer = db.query(CustomerModel).filter(CustomerModel.id == id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.put("/customers/{id}", response_model=Customer)
def update_customer(id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer"""
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.delete("/customers/{id}", status_code=204)
def delete_customer(id: int, db: Session = Depends(get_db)):
    """Delete a customer"""
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(db_customer)
    db.commit()
    return None


# Transaction Endpoints
@app.get("/transactions", response_model=List[Transaction])
def get_transactions(skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all transactions with optional filtering by customer_id"""
    query = db.query(TransactionModel)
    if customer_id:
        query = query.filter(TransactionModel.customer_id == customer_id)
    transactions = query.offset(skip).limit(limit).all()
    return transactions


@app.post("/transactions", response_model=Transaction, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction"""
    # Verify customer exists
    customer = db.query(CustomerModel).filter(CustomerModel.id == transaction.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db_transaction = TransactionModel(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/{id}", response_model=Transaction)
def get_transaction(id: int, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    transaction = db.query(TransactionModel).filter(TransactionModel.id == id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.put("/transactions/{id}", response_model=Transaction)
def update_transaction(id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)):
    """Update a transaction"""
    db_transaction = db.query(TransactionModel).filter(TransactionModel.id == id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction.dict(exclude_unset=True)
    
    # Verify customer exists if customer_id is being updated
    if "customer_id" in update_data:
        customer = db.query(CustomerModel).filter(CustomerModel.id == update_data["customer_id"]).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.delete("/transactions/{id}", status_code=204)
def delete_transaction(id: int, db: Session = Depends(get_db)):
    """Delete a transaction"""
    db_transaction = db.query(TransactionModel).filter(TransactionModel.id == id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(db_transaction)
    db.commit()
    return None


# Additional endpoints for Reports, Tasks, and Appointments
@app.get("/reports", response_model=List[Report])
def get_reports(skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all reports with optional filtering by customer_id"""
    query = db.query(ReportModel)
    if customer_id:
        query = query.filter(ReportModel.customer_id == customer_id)
    reports = query.offset(skip).limit(limit).all()
    return reports


@app.post("/reports", response_model=Report, status_code=201)
def create_report(report: ReportBase, db: Session = Depends(get_db)):
    """Create a new report"""
    customer = db.query(CustomerModel).filter(CustomerModel.id == report.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db_report = ReportModel(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@app.get("/tasks", response_model=List[Task])
def get_tasks(skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all tasks with optional filtering"""
    query = db.query(TaskModel)
    if customer_id:
        query = query.filter(TaskModel.customer_id == customer_id)
    if status:
        query = query.filter(TaskModel.status == status)
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskBase, db: Session = Depends(get_db)):
    """Create a new task"""
    customer = db.query(CustomerModel).filter(CustomerModel.id == task.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/appointments", response_model=List[Appointment])
def get_appointments(skip: int = 0, limit: int = 100, customer_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all appointments with optional filtering by customer_id"""
    query = db.query(AppointmentModel)
    if customer_id:
        query = query.filter(AppointmentModel.customer_id == customer_id)
    appointments = query.offset(skip).limit(limit).all()
    return appointments


@app.post("/appointments", response_model=Appointment, status_code=201)
def create_appointment(appointment: AppointmentBase, db: Session = Depends(get_db)):
    """Create a new appointment"""
    customer = db.query(CustomerModel).filter(CustomerModel.id == appointment.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db_appointment = AppointmentModel(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "FinCRM API"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)