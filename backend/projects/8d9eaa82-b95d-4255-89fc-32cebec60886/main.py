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
    
    products = relationship("Product", back_populates="owner")
    listings = relationship("Listing", back_populates="owner")
    transactions = relationship("Transaction", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    purchase_source = Column(String)
    quantity = Column(Integer, default=1)
    category = Column(String, index=True)
    condition = Column(String)
    sku = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="products")
    listings = relationship("Listing", back_populates="product")


class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String, nullable=False)  # eBay, Amazon
    title = Column(String, nullable=False)
    description = Column(Text)
    listing_price = Column(Float, nullable=False)
    status = Column(String, default="active")  # active, sold, inactive
    listing_url = Column(String)
    listing_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="listings")
    owner = relationship("User", back_populates="listings")
    sales = relationship("Sale", back_populates="listing")


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    buyer_info = Column(String)
    shipping_cost = Column(Float, default=0.0)
    platform_fees = Column(Float, default=0.0)
    profit = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    listing = relationship("Listing", back_populates="sales")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    transaction_type = Column(String, nullable=False)  # purchase, sale
    amount = Column(Float, nullable=False)
    description = Column(Text)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    purchase_price: float
    purchase_date: Optional[datetime] = None
    purchase_source: Optional[str] = None
    quantity: int = 1
    category: Optional[str] = None
    condition: Optional[str] = None
    sku: Optional[str] = None
    user_id: int = 1


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[datetime] = None
    purchase_source: Optional[str] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    sku: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ListingBase(BaseModel):
    product_id: int
    platform: str
    title: str
    description: Optional[str] = None
    listing_price: float
    status: str = "active"
    listing_url: Optional[str] = None
    listing_date: Optional[datetime] = None
    user_id: int = 1


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    product_id: Optional[int] = None
    platform: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    listing_price: Optional[float] = None
    status: Optional[str] = None
    listing_url: Optional[str] = None
    listing_date: Optional[datetime] = None


class ListingResponse(ListingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    listing_id: int
    sale_price: float
    sale_date: Optional[datetime] = None
    buyer_info: Optional[str] = None
    shipping_cost: float = 0.0
    platform_fees: float = 0.0
    profit: Optional[float] = None


class SaleCreate(SaleBase):
    pass


class SaleResponse(SaleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    total_products: int
    total_listings: int
    active_listings: int
    total_sales: int
    total_revenue: float
    total_profit: float
    average_profit_margin: float


# FastAPI app
app = FastAPI(
    title="Flippify API",
    description="A platform for facilitating the flipping of products on eBay and Amazon",
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


# Initialize default user
def init_default_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            default_user = User(
                id=1,
                username="default_user",
                email="user@flippify.com"
            )
            db.add(default_user)
            db.commit()
    finally:
        db.close()


init_default_user()


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Flippify API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Product endpoints
@app.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    products = query.offset(skip).limit(limit).all()
    return products


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    if product.sku:
        existing = db.query(Product).filter(Product.sku == product.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create transaction record
    transaction = Transaction(
        user_id=product.user_id,
        transaction_type="purchase",
        amount=product.purchase_price * product.quantity,
        description=f"Purchased {product.name}"
    )
    db.add(transaction)
    db.commit()
    
    return db_product


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    
    if "sku" in update_data and update_data["sku"]:
        existing = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product has active listings
    active_listings = db.query(Listing).filter(
        Listing.product_id == product_id,
        Listing.status == "active"
    ).count()
    
    if active_listings > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete product with active listings"
        )
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}


# Listing endpoints
@app.get("/listings", response_model=List[ListingResponse])
def get_listings(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all listings with optional filtering"""
    query = db.query(Listing)
    if platform:
        query = query.filter(Listing.platform == platform)
    if status:
        query = query.filter(Listing.status == status)
    listings = query.offset(skip).limit(limit).all()
    return listings


@app.post("/listings", response_model=ListingResponse, status_code=201)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    """Create a new listing"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == listing.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product has available quantity
    active_listings_count = db.query(Listing).filter(
        Listing.product_id == listing.product_id,
        Listing.status == "active"
    ).count()
    
    if active_listings_count >= product.quantity:
        raise HTTPException(
            status_code=400,
            detail="No available quantity for this product"
        )
    
    db_listing = Listing(**listing.model_dump())
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
    db_listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    update_data = listing_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_listing, field, value)
    
    db_listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_listing)
    return db_listing


@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    """Delete a listing"""
    db_listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Check if listing has sales
    sales_count = db.query(Sale).filter(Sale.listing_id == listing_id).count()
    if sales_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete listing with sales records"
        )
    
    db.delete(db_listing)
    db.commit()
    return {"message": "Listing deleted successfully"}


# Sales endpoints
@app.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all sales"""
    sales = db.query(Sale).offset(skip).limit(limit).all()
    return sales


@app.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale"""
    # Verify listing exists
    listing = db.query(Listing).filter(Listing.id == sale.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Get product to calculate profit
    product = db.query(Product).filter(Product.id == listing.product_id).first()
    
    # Calculate profit if not provided
    if sale.profit is None:
        sale.profit = (
            sale.sale_price - 
            product.purchase_price - 
            sale.shipping_cost - 
            sale.platform_fees
        )
    
    db_sale = Sale(**sale.model_dump())
    db.add(db_sale)
    
    # Update listing status to sold
    listing.status = "sold"
    
    # Create transaction record
    transaction = Transaction(
        user_id=listing.user_id,
        transaction_type="sale",
        amount=sale.sale_price,
        description=f"Sold {listing.title}"
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get a specific sale by ID"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


# Analytics endpoint
@app.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """Get sales analytics dashboard data"""
    total_products = db.query(Product).count()
    total_listings = db.query(Listing).count()
    active_listings = db.query(Listing).filter(Listing.status == "active").count()
    total_sales = db.query(Sale).count()
    
    sales = db.query(Sale).all()
    total_revenue = sum(sale.sale_price for sale in sales)
    total_profit = sum(sale.profit or 0 for sale in sales)
    
    average_profit_margin = 0
    if total_revenue > 0:
        average_profit_margin = (total_profit / total_revenue) * 100
    
    return {
        "total_products": total_products,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_sales": total_sales,
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "average_profit_margin": round(average_profit_margin, 2)
    }


# Price optimization endpoint
@app.get("/listings/{listing_id}/price-suggestion")
def get_price_suggestion(listing_id: int, db: Session = Depends(get_db)):
    """Get price optimization suggestion for a listing"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    product = db.query(Product).filter(Product.id == listing.product_id).first()
    
    # Simple price optimization logic
    cost = product.purchase_price
    current_price = listing.listing_price
    
    # Suggest 30-50% markup for healthy profit
    min_suggested = cost * 1.3
    max_suggested = cost * 1.5
    optimal_price = cost * 1.4
    
    # Platform-specific fee estimates
    platform_fee_rate = 0.13 if listing.platform.lower() == "amazon" else 0.10
    estimated_fees = optimal_price * platform_fee_rate
    estimated_profit = optimal_price - cost - estimated_fees
    
    return {
        "listing_id": listing_id,
        "current_price": current_price,
        "cost": cost,
        "suggested_price_range": {
            "min": round(min_suggested, 2),
            "max": round(max_suggested, 2),
            "optimal": round(optimal_price, 2)
        },
        "estimated_fees": round(estimated_fees, 2),
        "estimated_profit": round(estimated_profit, 2),
        "profit_margin": round((estimated_profit / optimal_price) * 100, 2)
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)