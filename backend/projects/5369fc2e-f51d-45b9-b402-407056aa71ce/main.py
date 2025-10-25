import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field

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
    sales = relationship("Sale", back_populates="seller")


class Platform(Base):
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    api_key = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("Item", back_populates="platform")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    purchase_price = Column(Float, nullable=False)
    suggested_price = Column(Float, nullable=True)
    listing_price = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    status = Column(String, default="available")  # available, listed, sold
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="items")
    platform = relationship("Platform", back_populates="items")
    sales = relationship("Sale", back_populates="item")


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    profit = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    buyer_info = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    item = relationship("Item", back_populates="sales")
    seller = relationship("User", back_populates="sales")


class Analytic(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    period = Column(String, nullable=True)  # daily, weekly, monthly
    recorded_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)


# Pydantic Schemas
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlatformBase(BaseModel):
    name: str
    api_key: Optional[str] = None
    is_active: Optional[int] = 1


class PlatformCreate(PlatformBase):
    pass


class PlatformResponse(PlatformBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    purchase_price: float = Field(..., gt=0)
    suggested_price: Optional[float] = None
    listing_price: Optional[float] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = "available"
    user_id: int
    platform_id: Optional[int] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    purchase_price: Optional[float] = None
    suggested_price: Optional[float] = None
    listing_price: Optional[float] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None
    platform_id: Optional[int] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    item_id: int
    user_id: int
    sale_price: float = Field(..., gt=0)
    fees: Optional[float] = 0.0
    profit: float
    buyer_info: Optional[str] = None
    notes: Optional[str] = None


class SaleCreate(BaseModel):
    item_id: int
    user_id: int
    sale_price: float = Field(..., gt=0)
    fees: Optional[float] = 0.0
    buyer_info: Optional[str] = None
    notes: Optional[str] = None


class SaleResponse(SaleBase):
    id: int
    sale_date: datetime
    
    class Config:
        from_attributes = True


class AnalyticResponse(BaseModel):
    id: int
    category: str
    metric_name: str
    metric_value: float
    period: Optional[str] = None
    recorded_at: datetime
    metadata: Optional[str] = None
    
    class Config:
        from_attributes = True


class AnalyticsOverview(BaseModel):
    total_items: int
    total_sales: int
    total_revenue: float
    total_profit: float
    average_profit_margin: float
    items_by_status: dict
    top_categories: List[dict]
    recent_sales: List[SaleResponse]


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    yield
    # Shutdown: cleanup if needed
    pass


# FastAPI app
app = FastAPI(
    title="Flippify API",
    description="A platform for users to easily flip and resell items on eBay and similar sites",
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


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Seed initial data
def seed_initial_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            return
        
        # Create default user
        default_user = User(
            username="demo_user",
            email="demo@flippify.com"
        )
        db.add(default_user)
        
        # Create platforms
        platforms = [
            Platform(name="eBay", is_active=1),
            Platform(name="Mercari", is_active=1),
            Platform(name="Poshmark", is_active=1),
            Platform(name="OfferUp", is_active=1),
        ]
        for platform in platforms:
            db.add(platform)
        
        db.commit()
        
        # Create sample items
        sample_items = [
            Item(
                title="Vintage Nike Sneakers",
                description="Rare vintage Nike sneakers in excellent condition",
                purchase_price=45.00,
                suggested_price=120.00,
                listing_price=115.00,
                category="Shoes",
                condition="Used - Excellent",
                status="listed",
                user_id=1,
                platform_id=1
            ),
            Item(
                title="iPhone 12 Pro",
                description="Unlocked iPhone 12 Pro, 128GB",
                purchase_price=350.00,
                suggested_price=550.00,
                listing_price=525.00,
                category="Electronics",
                condition="Used - Good",
                status="available",
                user_id=1,
                platform_id=1
            ),
            Item(
                title="Designer Handbag",
                description="Authentic Michael Kors handbag",
                purchase_price=80.00,
                suggested_price=180.00,
                listing_price=175.00,
                category="Fashion",
                condition="Used - Like New",
                status="sold",
                user_id=1,
                platform_id=3
            ),
        ]
        for item in sample_items:
            db.add(item)
        
        db.commit()
        
        # Create sample sale
        sample_sale = Sale(
            item_id=3,
            user_id=1,
            sale_price=175.00,
            fees=17.50,
            profit=77.50,
            buyer_info="buyer123",
            notes="Quick sale, great buyer"
        )
        db.add(sample_sale)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()


# Helper function to calculate suggested price
def calculate_suggested_price(purchase_price: float, category: Optional[str] = None) -> float:
    """Calculate suggested price based on purchase price and category"""
    base_markup = 2.0  # 100% markup
    
    category_multipliers = {
        "Electronics": 1.5,
        "Shoes": 2.5,
        "Fashion": 2.2,
        "Collectibles": 3.0,
        "Home & Garden": 1.8,
        "Toys": 2.0,
    }
    
    multiplier = category_multipliers.get(category, base_markup)
    return round(purchase_price * multiplier, 2)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Flippify API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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


# Platform endpoints
@app.post("/platforms", response_model=PlatformResponse, status_code=201)
def create_platform(platform: PlatformCreate, db: Session = Depends(get_db)):
    """Create a new platform"""
    db_platform = Platform(**platform.dict())
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform


@app.get("/platforms", response_model=List[PlatformResponse])
def get_platforms(db: Session = Depends(get_db)):
    """Get all platforms"""
    platforms = db.query(Platform).all()
    return platforms


# Item endpoints
@app.get("/items", response_model=List[ItemResponse])
def get_items(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all items with optional filters"""
    query = db.query(Item)
    
    if status:
        query = query.filter(Item.status == status)
    if category:
        query = query.filter(Item.category == category)
    if user_id:
        query = query.filter(Item.user_id == user_id)
    
    items = query.offset(skip).limit(limit).all()
    return items


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    # Verify user exists
    user = db.query(User).filter(User.id == item.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify platform exists if provided
    if item.platform_id:
        platform = db.query(Platform).filter(Platform.id == item.platform_id).first()
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
    
    # Calculate suggested price if not provided
    item_data = item.dict()
    if not item_data.get("suggested_price"):
        item_data["suggested_price"] = calculate_suggested_price(
            item.purchase_price,
            item.category
        )
    
    db_item = Item(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


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
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    
    # Recalculate suggested price if purchase price or category changed
    if "purchase_price" in update_data or "category" in update_data:
        purchase_price = update_data.get("purchase_price", db_item.purchase_price)
        category = update_data.get("category", db_item.category)
        update_data["suggested_price"] = calculate_suggested_price(purchase_price, category)
    
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return None


# Sales endpoints
@app.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all sales with optional filters"""
    query = db.query(Sale)
    
    if user_id:
        query = query.filter(Sale.user_id == user_id)
    
    sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    return sales


@app.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale"""
    # Verify item exists
    item = db.query(Item).filter(Item.id == sale.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == sale.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate profit
    profit = sale.sale_price - sale.fees - item.purchase_price
    
    # Create sale
    db_sale = Sale(
        item_id=sale.item_id,
        user_id=sale.user_id,
        sale_price=sale.sale_price,
        fees=sale.fees,
        profit=profit,
        buyer_info=sale.buyer_info,
        notes=sale.notes
    )
    db.add(db_sale)
    
    # Update item status to sold
    item.status = "sold"
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get a specific sale"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


# Analytics endpoints
@app.get("/analytics", response_model=AnalyticsOverview)
def get_analytics(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get analytics overview"""
    # Base queries
    items_query = db.query(Item)
    sales_query = db.query(Sale)
    
    if user_id:
        items_query = items_query.filter(Item.user_id == user_id)
        sales_query = sales_query.filter(Sale.user_id == user_id)
    
    # Total items
    total_items = items_query.count()
    
    # Total sales
    total_sales = sales_query.count()
    
    # Total revenue and profit
    sales_data = sales_query.all()
    total_revenue = sum(sale.sale_price for sale in sales_data)
    total_profit = sum(sale.profit for sale in sales_data)
    
    # Average profit margin
    if total_revenue > 0:
        average_profit_margin = round((total_profit / total_revenue) * 100, 2)
    else:
        average_profit_margin = 0.0
    
    # Items by status
    status_counts = db.query(
        Item.status,
        func.count(Item.id)
    ).group_by(Item.status)
    
    if user_id:
        status_counts = status_counts.filter(Item.user_id == user_id)
    
    items_by_status = {status: count for status, count in status_counts.all()}
    
    # Top categories by profit
    top_categories_data = db.query(
        Item.category,
        func.sum(Sale.profit).label("total_profit"),
        func.count(Sale.id).label("sales_count")
    ).join(Sale, Item.id == Sale.item_id).group_by(Item.category)
    
    if user_id:
        top_categories_data = top_categories_data.filter(Item.user_id == user_id)
    
    top_categories = [
        {
            "category": category or "Uncategorized",
            "total_profit": float(profit or 0),
            "sales_count": count
        }
        for category, profit, count in top_categories_data.order_by(func.sum(Sale.profit).desc()).limit(5).all()
    ]
    
    # Recent sales
    recent_sales_query = sales_query.order_by(Sale.sale_date.desc()).limit(10)
    recent_sales = recent_sales_query.all()
    
    return AnalyticsOverview(
        total_items=total_items,
        total_sales=total_sales,
        total_revenue=round(total_revenue, 2),
        total_profit=round(total_profit, 2),
        average_profit_margin=average_profit_margin,
        items_by_status=items_by_status,
        top_categories=top_categories,
        recent_sales=recent_sales
    )


@app.get("/analytics/trends")
def get_trends(
    category: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get market trends and pricing data"""
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Sales trends over time
    sales_query = db.query(
        func.date(Sale.sale_date).label("date"),
        func.count(Sale.id).label("count"),
        func.sum(Sale.sale_price).label("revenue"),
        func.sum(Sale.profit).label("profit")
    ).filter(Sale.sale_date >= cutoff_date).group_by(func.date(Sale.sale_date))
    
    sales_trends = [
        {
            "date": str(date),
            "count": count,
            "revenue": float(revenue or 0),
            "profit": float(profit or 0)
        }
        for date, count, revenue, profit in sales_query.all()
    ]
    
    # Category performance
    category_query = db.query(
        Item.category,
        func.avg(Sale.profit).label("avg_profit"),
        func.avg(Sale.sale_price).label("avg_sale_price"),
        func.count(Sale.id).label("sales_count")
    ).join(Sale, Item.id == Sale.item_id).filter(Sale.sale_date >= cutoff_date)
    
    if category:
        category_query = category_query.filter(Item.category == category)
    
    category_query = category_query.group_by(Item.category)
    
    category_performance = [
        {
            "category": cat or "Uncategorized",
            "avg_profit": round(float(avg_profit or 0), 2),
            "avg_sale_price": round(float(avg_sale_price or 0), 2),
            "sales_count": sales_count
        }
        for cat, avg_profit, avg_sale_price, sales_count in category_query.all()
    ]
    
    # Price recommendations by category
    price_recommendations = {}
    categories = db.query(Item.category).distinct().all()
    
    for (cat,) in categories:
        if cat:
            avg_markup = db.query(
                func.avg((Sale.sale_price - Item.purchase_price) / Item.purchase_price * 100)
            ).join(Sale, Item.id == Sale.item_id).filter(
                Item.category == cat,
                Sale.sale_date >= cutoff_date
            ).scalar()
            
            if avg_markup:
                price_recommendations[cat] = {
                    "avg_markup_percentage": round(float(avg_markup), 2),
                    "recommended_multiplier": round(1 + (float(avg_markup) / 100), 2)
                }
    
    return {
        "period_days": days,
        "sales_trends": sales_trends,
        "category_performance": category_performance,
        "price_recommendations": price_recommendations
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)