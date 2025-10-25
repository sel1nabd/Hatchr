import os
from datetime import date, datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./ftracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    description = Column(String, nullable=True)
    
    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    category_id: int
    date: date
    description: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    date: Optional[date] = None
    description: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int
    category: CategoryResponse
    
    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    user_id: int
    category_id: int
    amount: float = Field(gt=0)
    period_start: date
    period_end: date


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class BudgetResponse(BudgetBase):
    id: int
    category: CategoryResponse
    
    class Config:
        from_attributes = True


class BudgetStatusResponse(BudgetResponse):
    spent: float
    remaining: float
    percentage_used: float
    
    class Config:
        from_attributes = True


class SpendingInsight(BaseModel):
    category: str
    total_spent: float
    transaction_count: int
    percentage_of_total: float


class SpendingReport(BaseModel):
    total_expenses: float
    period_start: date
    period_end: date
    category_breakdown: List[SpendingInsight]


# FastAPI app
app = FastAPI(
    title="F-Tracker API",
    description="Personal Finance Tracking Application",
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


# Initialize default categories
def init_default_data(db: Session):
    if db.query(Category).count() == 0:
        default_categories = [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Education",
            "Travel",
            "Personal Care",
            "Other"
        ]
        for cat_name in default_categories:
            category = Category(name=cat_name)
            db.add(category)
        db.commit()
    
    if db.query(User).count() == 0:
        default_user = User(name="Demo User", email="demo@ftracker.com")
        db.add(default_user)
        db.commit()


# Initialize data on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        init_default_data(db)
    finally:
        db.close()


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to F-Tracker API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# User endpoints
@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Category endpoints
@app.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


@app.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Expense endpoints
@app.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Expense)
    
    if user_id:
        query = query.filter(Expense.user_id == user_id)
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()
    return expenses


@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == expense.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == expense.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_expense = Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense_update: ExpenseUpdate, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = expense_update.dict(exclude_unset=True)
    
    # Verify category if being updated
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    for field, value in update_data.items():
        setattr(db_expense, field, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(db_expense)
    db.commit()
    return None


# Budget endpoints
@app.get("/budgets", response_model=List[BudgetResponse])
def get_budgets(
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Budget)
    
    if user_id:
        query = query.filter(Budget.user_id == user_id)
    if category_id:
        query = query.filter(Budget.category_id == category_id)
    if active_only:
        today = date.today()
        query = query.filter(Budget.period_start <= today, Budget.period_end >= today)
    
    budgets = query.order_by(Budget.period_start.desc()).all()
    return budgets


@app.post("/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == budget.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == budget.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate dates
    if budget.period_end <= budget.period_start:
        raise HTTPException(status_code=400, detail="Period end must be after period start")
    
    db_budget = Budget(**budget.dict())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.get("/budgets/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@app.put("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, budget_update: BudgetUpdate, db: Session = Depends(get_db)):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    update_data = budget_update.dict(exclude_unset=True)
    
    # Verify category if being updated
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    
    # Validate dates if both are present
    if db_budget.period_end <= db_budget.period_start:
        raise HTTPException(status_code=400, detail="Period end must be after period start")
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.delete("/budgets/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(db_budget)
    db.commit()
    return None


# Budget status endpoint
@app.get("/budgets/{budget_id}/status", response_model=BudgetStatusResponse)
def get_budget_status(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Calculate total spent in the budget period
    spent = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == budget.user_id,
        Expense.category_id == budget.category_id,
        Expense.date >= budget.period_start,
        Expense.date <= budget.period_end
    ).scalar() or 0.0
    
    remaining = budget.amount - spent
    percentage_used = (spent / budget.amount * 100) if budget.amount > 0 else 0
    
    return {
        **BudgetResponse.from_orm(budget).dict(),
        "spent": spent,
        "remaining": remaining,
        "percentage_used": round(percentage_used, 2)
    }


# Spending insights endpoint
@app.get("/insights/spending", response_model=SpendingReport)
def get_spending_insights(
    user_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Get total expenses
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).scalar() or 0.0
    
    # Get category breakdown
    category_data = db.query(
        Category.name,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count")
    ).join(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).group_by(Category.id).all()
    
    category_breakdown = []
    for cat_name, total, count in category_data:
        percentage = (total / total_expenses * 100) if total_expenses > 0 else 0
        category_breakdown.append(
            SpendingInsight(
                category=cat_name,
                total_spent=round(total, 2),
                transaction_count=count,
                percentage_of_total=round(percentage, 2)
            )
        )
    
    # Sort by total spent descending
    category_breakdown.sort(key=lambda x: x.total_spent, reverse=True)
    
    return SpendingReport(
        total_expenses=round(total_expenses, 2),
        period_start=start_date,
        period_end=end_date,
        category_breakdown=category_breakdown
    )


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "F-Tracker API"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)