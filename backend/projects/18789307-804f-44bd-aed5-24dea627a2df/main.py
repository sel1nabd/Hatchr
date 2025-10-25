import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./devfinance_crm.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    clients = relationship("Client", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    projects = relationship("Project", back_populates="user")


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    address = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")
    projects = relationship("Project", back_populates="client")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, paid, overdue, cancelled
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    description = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    receipt_url = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="expenses")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")  # active, completed, on_hold, cancelled
    hourly_rate = Column(Float)
    hours_tracked = Column(Float, default=0.0)
    budget = Column(Float)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    client = relationship("Client", back_populates="projects")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    user_id: int = Field(default=1, description="User ID (defaults to 1 for demo)")


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    invoice_number: str
    amount: float = Field(gt=0, description="Invoice amount must be greater than 0")
    status: str = Field(default="pending", pattern="^(pending|paid|overdue|cancelled)$")
    due_date: datetime
    description: Optional[str] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    user_id: int = Field(default=1, description="User ID (defaults to 1 for demo)")
    client_id: int


class InvoiceResponse(InvoiceBase):
    id: int
    user_id: int
    client_id: int
    issue_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    category: str
    amount: float = Field(gt=0, description="Expense amount must be greater than 0")
    description: str
    date: Optional[datetime] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    user_id: int = Field(default=1, description="User ID (defaults to 1 for demo)")


class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|completed|on_hold|cancelled)$")
    hourly_rate: Optional[float] = Field(None, gt=0)
    hours_tracked: float = Field(default=0.0, ge=0)
    budget: Optional[float] = Field(None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    user_id: int = Field(default=1, description="User ID (defaults to 1 for demo)")
    client_id: int


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|on_hold|cancelled)$")
    hourly_rate: Optional[float] = Field(None, gt=0)
    hours_tracked: Optional[float] = Field(None, ge=0)
    budget: Optional[float] = Field(None, gt=0)
    end_date: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    client_id: int
    start_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class FinancialReportResponse(BaseModel):
    total_revenue: float
    total_expenses: float
    net_income: float
    pending_invoices: float
    paid_invoices: float
    total_invoices: int
    total_expenses_count: int
    active_projects: int
    total_clients: int


# FastAPI App
app = FastAPI(
    title="DevFinance CRM",
    description="A financial CRM tailored for software developers to manage their finances and client interactions",
    version="1.0.0"
)

# CORS Middleware
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


# Initialize demo user
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            demo_user = User(
                id=1,
                name="Demo Developer",
                email="demo@devfinance.com",
                phone="+1-555-0100",
                company="DevFinance Demo"
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to DevFinance CRM API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "clients": "/clients",
            "invoices": "/invoices",
            "expenses": "/expenses",
            "projects": "/projects",
            "financial_report": "/financial-report"
        }
    }


# Client Endpoints
@app.get("/clients", response_model=List[ClientResponse])
async def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all clients"""
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients


@app.post("/clients", response_model=ClientResponse, status_code=201)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    # Check if user exists
    user = db.query(User).filter(User.id == client.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {client.user_id} not found")
    
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@app.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    """Update a client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@app.delete("/clients/{client_id}", status_code=204)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return None


# Invoice Endpoints
@app.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all invoices with optional filters"""
    query = db.query(Invoice)
    
    if status:
        query = query.filter(Invoice.status == status)
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices


@app.post("/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    """Create a new invoice"""
    # Check if user exists
    user = db.query(User).filter(User.id == invoice.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {invoice.user_id} not found")
    
    # Check if client exists
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail=f"Client with id {invoice.client_id} not found")
    
    # Check if invoice number already exists
    existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice.invoice_number).first()
    if existing_invoice:
        raise HTTPException(status_code=400, detail="Invoice number already exists")
    
    db_invoice = Invoice(**invoice.model_dump())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get a specific invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@app.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: int,
    status: str = Field(..., pattern="^(pending|paid|overdue|cancelled)$"),
    db: Session = Depends(get_db)
):
    """Update invoice status"""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    db_invoice.status = status
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


# Expense Endpoints
@app.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all expenses with optional category filter"""
    query = db.query(Expense)
    
    if category:
        query = query.filter(Expense.category == category)
    
    expenses = query.offset(skip).limit(limit).all()
    return expenses


@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
async def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense"""
    # Check if user exists
    user = db.query(User).filter(User.id == expense.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {expense.user_id} not found")
    
    expense_data = expense.model_dump()
    if expense_data.get('date') is None:
        expense_data['date'] = datetime.utcnow()
    
    db_expense = Expense(**expense_data)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a specific expense by ID"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(db_expense)
    db.commit()
    return None


# Project Endpoints
@app.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all projects with optional filters"""
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    if client_id:
        query = query.filter(Project.client_id == client_id)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@app.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    # Check if user exists
    user = db.query(User).filter(User.id == project.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {project.user_id} not found")
    
    # Check if client exists
    client = db.query(Client).filter(Client.id == project.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail=f"Client with id {project.client_id} not found")
    
    project_data = project.model_dump()
    if project_data.get('start_date') is None:
        project_data['start_date'] = datetime.utcnow()
    
    db_project = Project(**project_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


@app.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return None


# Financial Reporting Endpoint
@app.get("/financial-report", response_model=FinancialReportResponse)
async def get_financial_report(user_id: int = 1, db: Session = Depends(get_db)):
    """Get comprehensive financial report"""
    # Calculate total revenue from paid invoices
    paid_invoices = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.status == "paid"
    ).all()
    total_revenue = sum(inv.amount for inv in paid_invoices)
    paid_invoices_amount = total_revenue
    
    # Calculate pending invoices
    pending_invoices = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.status == "pending"
    ).all()
    pending_invoices_amount = sum(inv.amount for inv in pending_invoices)
    
    # Calculate total expenses
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    total_expenses = sum(exp.amount for exp in expenses)
    
    # Calculate net income
    net_income = total_revenue - total_expenses
    
    # Count total invoices
    total_invoices = db.query(Invoice).filter(Invoice.user_id == user_id).count()
    
    # Count total expenses
    total_expenses_count = len(expenses)
    
    # Count active projects
    active_projects = db.query(Project).filter(
        Project.user_id == user_id,
        Project.status == "active"
    ).count()
    
    # Count total clients
    total_clients = db.query(Client).filter(Client.user_id == user_id).count()
    
    return FinancialReportResponse(
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_income=net_income,
        pending_invoices=pending_invoices_amount,
        paid_invoices=paid_invoices_amount,
        total_invoices=total_invoices,
        total_expenses_count=total_expenses_count,
        active_projects=active_projects,
        total_clients=total_clients
    )


# User Endpoints (bonus)
@app.get("/users", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DevFinance CRM API"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)