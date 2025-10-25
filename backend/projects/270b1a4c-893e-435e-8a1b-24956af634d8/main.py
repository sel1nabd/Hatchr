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
DATABASE_URL = "sqlite:///./flippify.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("Item", back_populates="owner")
    reviews = relationship("Review", back_populates="reviewer")
    analytics = relationship("Analytics", back_populates="user", uselist=False)


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    purchase_source = Column(String, nullable=False)  # eBay, Amazon, etc.
    purchase_price = Column(Float, nullable=False)
    resale_price = Column(Float)
    suggested_price = Column(Float)
    status = Column(String, default="available")  # available, sold, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="items")
    sales = relationship("Sale", back_populates="item")
    reviews = relationship("Review", back_populates="item")


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    buyer_name = Column(String)
    profit = Column(Float)
    
    item = relationship("Item", back_populates="sales")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    item = relationship("Item", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    items_listed = Column(Integer, default=0)
    items_sold = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="analytics")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    purchase_source: str
    purchase_price: float
    resale_price: Optional[float] = None
    status: Optional[str] = "available"


class ItemCreate(ItemBase):
    user_id: int


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    purchase_source: Optional[str] = None
    purchase_price: Optional[float] = None
    resale_price: Optional[float] = None
    status: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    user_id: int
    suggested_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    item_id: int
    sale_price: float
    buyer_name: Optional[str] = None


class SaleCreate(SaleBase):
    pass


class SaleResponse(SaleBase):
    id: int
    sale_date: datetime
    profit: Optional[float] = None
    
    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    item_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    id: int
    user_id: int
    total_sales: int
    total_revenue: float
    total_profit: float
    items_listed: int
    items_sold: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="Flippify API",
    description="A platform for reselling items bought on eBay and Amazon",
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


# Helper function to calculate suggested price
def calculate_suggested_price(purchase_price: float, purchase_source: str) -> float:
    """Calculate suggested resale price based on purchase price and source"""
    markup_rates = {
        "ebay": 1.3,
        "amazon": 1.25,
        "other": 1.35
    }
    source_key = purchase_source.lower()
    markup = markup_rates.get(source_key, markup_rates["other"])
    return round(purchase_price * markup, 2)


# Helper function to update analytics
def update_user_analytics(db: Session, user_id: int):
    """Update analytics for a user"""
    analytics = db.query(Analytics).filter(Analytics.user_id == user_id).first()
    
    if not analytics:
        analytics = Analytics(user_id=user_id)
        db.add(analytics)
    
    # Count items
    items = db.query(Item).filter(Item.user_id == user_id).all()
    analytics.items_listed = len(items)
    analytics.items_sold = len([i for i in items if i.status == "sold"])
    
    # Calculate sales and revenue
    sales = db.query(Sale).join(Item).filter(Item.user_id == user_id).all()
    analytics.total_sales = len(sales)
    analytics.total_revenue = sum(sale.sale_price for sale in sales)
    analytics.total_profit = sum(sale.profit for sale in sales if sale.profit)
    
    db.commit()
    db.refresh(analytics)
    return analytics


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Flippify API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create analytics entry
    analytics = Analytics(user_id=new_user.id)
    db.add(analytics)
    db.commit()
    
    return new_user


@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Item endpoints
@app.get("/items", response_model=List[ItemResponse])
def get_items(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all items with optional filters"""
    query = db.query(Item)
    
    if status:
        query = query.filter(Item.status == status)
    if user_id:
        query = query.filter(Item.user_id == user_id)
    
    items = query.offset(skip).limit(limit).all()
    return items


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item listing"""
    # Verify user exists
    user = db.query(User).filter(User.id == item.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate suggested price
    suggested_price = calculate_suggested_price(item.purchase_price, item.purchase_source)
    
    new_item = Item(**item.dict(), suggested_price=suggested_price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Update analytics
    update_user_analytics(db, item.user_id)
    
    return new_item


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    """Update an item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    
    # Recalculate suggested price if purchase price or source changed
    if "purchase_price" in update_data or "purchase_source" in update_data:
        purchase_price = update_data.get("purchase_price", item.purchase_price)
        purchase_source = update_data.get("purchase_source", item.purchase_source)
        update_data["suggested_price"] = calculate_suggested_price(purchase_price, purchase_source)
    
    for key, value in update_data.items():
        setattr(item, key, value)
    
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    
    # Update analytics if status changed
    if "status" in update_data:
        update_user_analytics(db, item.user_id)
    
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    user_id = item.user_id
    db.delete(item)
    db.commit()
    
    # Update analytics
    update_user_analytics(db, user_id)
    
    return None


# Sale endpoints
@app.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    item_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all sales with optional filters"""
    query = db.query(Sale)
    
    if item_id:
        query = query.filter(Sale.item_id == item_id)
    
    sales = query.offset(skip).limit(limit).all()
    return sales


@app.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Record a new sale"""
    # Verify item exists
    item = db.query(Item).filter(Item.id == sale.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.status == "sold":
        raise HTTPException(status_code=400, detail="Item already sold")
    
    # Calculate profit
    profit = sale.sale_price - item.purchase_price
    
    new_sale = Sale(**sale.dict(), profit=profit)
    db.add(new_sale)
    
    # Update item status
    item.status = "sold"
    item.resale_price = sale.sale_price
    
    db.commit()
    db.refresh(new_sale)
    
    # Update analytics
    update_user_analytics(db, item.user_id)
    
    return new_sale


@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get a specific sale"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


# Review endpoints
@app.get("/reviews", response_model=List[ReviewResponse])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    item_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all reviews with optional filters"""
    query = db.query(Review)
    
    if item_id:
        query = query.filter(Review.item_id == item_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews


@app.post("/reviews", response_model=ReviewResponse, status_code=201)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review"""
    # Verify item exists
    item = db.query(Item).filter(Item.id == review.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == review.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_review = Review(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return new_review


@app.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get a specific review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


# Analytics endpoints
@app.get("/analytics/{user_id}", response_model=AnalyticsResponse)
def get_user_analytics(user_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = update_user_analytics(db, user_id)
    return analytics


@app.get("/analytics", response_model=List[AnalyticsResponse])
def get_all_analytics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get analytics for all users"""
    analytics = db.query(Analytics).offset(skip).limit(limit).all()
    return analytics


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)