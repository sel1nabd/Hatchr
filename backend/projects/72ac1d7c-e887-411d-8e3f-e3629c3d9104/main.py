import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field
import uvicorn

# Database setup
DATABASE_URL = "sqlite:///./flipify.db"
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
    
    listings = relationship("Listing", back_populates="user")
    inventory = relationship("Inventory", back_populates="user")
    sales = relationship("Sale", back_populates="user")


class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    optimized_price = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    platform = Column(String, default="eBay")
    status = Column(String, default="active")
    ebay_listing_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="listings")
    inventory = relationship("Inventory", back_populates="listings")


class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    purchase_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    category = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, default="available")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="inventory")
    listings = relationship("Listing", back_populates="inventory")


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    sale_price = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    platform = Column(String, default="eBay")
    buyer_info = Column(String, nullable=True)
    sale_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sales")


class Analytic(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String, nullable=False)
    period = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
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


class ListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    condition: Optional[str] = None
    platform: str = "eBay"
    inventory_id: Optional[int] = None


class ListingCreate(ListingBase):
    user_id: int = 1


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    optimized_price: Optional[float] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None


class ListingResponse(ListingBase):
    id: int
    user_id: int
    optimized_price: Optional[float] = None
    status: str
    ebay_listing_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    purchase_price: float
    quantity: int = 1
    category: Optional[str] = None
    condition: Optional[str] = None
    location: Optional[str] = None


class InventoryCreate(InventoryBase):
    user_id: int = 1


class InventoryResponse(InventoryBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    sale_price: float
    purchase_price: float
    platform: str = "eBay"
    buyer_info: Optional[str] = None


class SaleCreate(SaleBase):
    user_id: int = 1
    listing_id: Optional[int] = None
    inventory_id: Optional[int] = None


class SaleResponse(SaleBase):
    id: int
    user_id: int
    listing_id: Optional[int] = None
    inventory_id: Optional[int] = None
    profit: float
    sale_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticResponse(BaseModel):
    id: int
    user_id: int
    metric_name: str
    metric_value: float
    metric_type: str
    period: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_sales: int
    total_revenue: float
    total_profit: float
    average_profit_margin: float
    active_listings: int
    total_inventory_items: int
    inventory_value: float


# FastAPI app
app = FastAPI(
    title="Flipify API",
    description="A tool to streamline and optimize the process of reselling products on eBay",
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


# Helper function to create default user if not exists
def ensure_default_user(db: Session):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(username="default_user", email="default@flipify.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# Helper function for price optimization
def optimize_price(purchase_price: float, category: Optional[str] = None) -> float:
    """Simple price optimization algorithm based on desired profit margin"""
    base_margin = 0.30  # 30% profit margin
    category_multipliers = {
        "electronics": 1.2,
        "clothing": 1.5,
        "collectibles": 1.8,
        "books": 1.3,
        "toys": 1.4,
    }
    
    multiplier = category_multipliers.get(category.lower() if category else "", 1.0)
    optimized = purchase_price * (1 + base_margin) * multiplier
    return round(optimized, 2)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Flipify API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Listings endpoints
@app.get("/listings", response_model=List[ListingResponse])
def get_listings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all listings with optional filtering"""
    query = db.query(Listing)
    if status:
        query = query.filter(Listing.status == status)
    listings = query.offset(skip).limit(limit).all()
    return listings


@app.post("/listings", response_model=ListingResponse, status_code=201)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    """Create a new listing with automatic price optimization"""
    ensure_default_user(db)
    
    # Get purchase price from inventory if linked
    purchase_price = 0
    if listing.inventory_id:
        inventory_item = db.query(Inventory).filter(Inventory.id == listing.inventory_id).first()
        if inventory_item:
            purchase_price = inventory_item.purchase_price
    
    # Calculate optimized price
    optimized_price = optimize_price(
        purchase_price if purchase_price > 0 else listing.price * 0.7,
        listing.category
    )
    
    # Generate mock eBay listing ID
    ebay_listing_id = f"EBAY-{datetime.utcnow().timestamp()}"
    
    db_listing = Listing(
        **listing.dict(),
        optimized_price=optimized_price,
        ebay_listing_id=ebay_listing_id
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


@app.get("/listings/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a specific listing by ID"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@app.put("/listings/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    listing_update: ListingUpdate,
    db: Session = Depends(get_db)
):
    """Update a listing"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    update_data = listing_update.dict(exclude_unset=True)
    
    # Recalculate optimized price if price is updated
    if "price" in update_data:
        update_data["optimized_price"] = optimize_price(
            update_data["price"] * 0.7,
            listing.category
        )
    
    for key, value in update_data.items():
        setattr(listing, key, value)
    
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    return listing


@app.delete("/listings/{listing_id}", status_code=204)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    """Delete a listing"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    db.delete(listing)
    db.commit()
    return None


# Inventory endpoints
@app.get("/inventory", response_model=List[InventoryResponse])
def get_inventory(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all inventory items"""
    query = db.query(Inventory)
    if status:
        query = query.filter(Inventory.status == status)
    inventory = query.offset(skip).limit(limit).all()
    return inventory


@app.post("/inventory", response_model=InventoryResponse, status_code=201)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    """Add a new inventory item"""
    ensure_default_user(db)
    
    # Check if SKU already exists
    existing = db.query(Inventory).filter(Inventory.sku == inventory.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@app.get("/inventory/{inventory_id}", response_model=InventoryResponse)
def get_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Get a specific inventory item"""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory


# Sales endpoints
@app.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all sales records"""
    query = db.query(Sale)
    if platform:
        query = query.filter(Sale.platform == platform)
    sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    return sales


@app.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Record a new sale"""
    ensure_default_user(db)
    
    # Calculate profit
    profit = sale.sale_price - sale.purchase_price
    
    db_sale = Sale(**sale.dict(), profit=profit)
    db.add(db_sale)
    
    # Update listing status if linked
    if sale.listing_id:
        listing = db.query(Listing).filter(Listing.id == sale.listing_id).first()
        if listing:
            listing.status = "sold"
    
    # Update inventory status if linked
    if sale.inventory_id:
        inventory = db.query(Inventory).filter(Inventory.id == sale.inventory_id).first()
        if inventory:
            inventory.quantity -= 1
            if inventory.quantity <= 0:
                inventory.status = "sold"
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


# Analytics endpoints
@app.get("/analytics", response_model=AnalyticsSummary)
def get_analytics(db: Session = Depends(get_db)):
    """Get comprehensive sales and performance analytics"""
    
    # Total sales
    total_sales = db.query(Sale).count()
    
    # Total revenue and profit
    sales = db.query(Sale).all()
    total_revenue = sum(sale.sale_price for sale in sales)
    total_profit = sum(sale.profit for sale in sales)
    
    # Average profit margin
    average_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Active listings
    active_listings = db.query(Listing).filter(Listing.status == "active").count()
    
    # Total inventory items
    total_inventory_items = db.query(Inventory).filter(Inventory.status == "available").count()
    
    # Inventory value
    inventory_items = db.query(Inventory).filter(Inventory.status == "available").all()
    inventory_value = sum(item.purchase_price * item.quantity for item in inventory_items)
    
    return AnalyticsSummary(
        total_sales=total_sales,
        total_revenue=round(total_revenue, 2),
        total_profit=round(total_profit, 2),
        average_profit_margin=round(average_profit_margin, 2),
        active_listings=active_listings,
        total_inventory_items=total_inventory_items,
        inventory_value=round(inventory_value, 2)
    )


@app.get("/analytics/detailed", response_model=List[AnalyticResponse])
def get_detailed_analytics(
    skip: int = 0,
    limit: int = 100,
    metric_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get detailed analytics records"""
    query = db.query(Analytic)
    if metric_type:
        query = query.filter(Analytic.metric_type == metric_type)
    analytics = query.order_by(Analytic.created_at.desc()).offset(skip).limit(limit).all()
    return analytics


# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)