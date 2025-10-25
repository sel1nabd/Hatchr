import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
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
    
    products = relationship("Product", back_populates="user")
    listings = relationship("Listing", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    source_platform = Column(String, nullable=False)  # eBay or Amazon
    source_url = Column(String)
    source_price = Column(Float, nullable=False)
    target_platform = Column(String, nullable=False)  # eBay or Amazon
    category = Column(String)
    sku = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=1)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="products")
    listings = relationship("Listing", back_populates="product")
    pricing_rules = relationship("PricingRule", back_populates="product")


class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String, nullable=False)  # eBay or Amazon
    listing_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String, default="active")  # active, paused, sold, ended
    listing_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="listings")
    product = relationship("Product", back_populates="listings")
    sales = relationship("SalesAnalytic", back_populates="listing")


class PricingRule(Base):
    __tablename__ = "pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rule_name = Column(String, nullable=False)
    markup_percentage = Column(Float, default=0.0)
    markup_fixed = Column(Float, default=0.0)
    min_price = Column(Float)
    max_price = Column(Float)
    auto_reprice = Column(Boolean, default=False)
    competitor_price_check = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="pricing_rules")


class SalesAnalytic(Base):
    __tablename__ = "sales_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    sale_price = Column(Float, nullable=False)
    quantity_sold = Column(Integer, default=1)
    platform_fees = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    profit = Column(Float, nullable=False)
    buyer_location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    listing = relationship("Listing", back_populates="sales")


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


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    source_platform: str
    source_url: Optional[str] = None
    source_price: float
    target_platform: str
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: int = 1
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    user_id: int = 1  # Default user for simplicity


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    source_price: Optional[float] = None
    target_platform: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = None
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ListingBase(BaseModel):
    platform: str
    listing_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: float
    quantity: int = 1
    status: str = "active"
    listing_url: Optional[str] = None


class ListingCreate(ListingBase):
    user_id: int = 1  # Default user for simplicity
    product_id: int


class ListingUpdate(BaseModel):
    platform: Optional[str] = None
    listing_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    listing_url: Optional[str] = None


class ListingResponse(ListingBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PricingRuleBase(BaseModel):
    rule_name: str
    markup_percentage: float = 0.0
    markup_fixed: float = 0.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    auto_reprice: bool = False
    competitor_price_check: bool = False


class PricingRuleCreate(PricingRuleBase):
    product_id: int


class PricingRuleResponse(PricingRuleBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SalesAnalyticBase(BaseModel):
    sale_price: float
    quantity_sold: int = 1
    platform_fees: float = 0.0
    shipping_cost: float = 0.0
    profit: float
    buyer_location: Optional[str] = None


class SalesAnalyticCreate(SalesAnalyticBase):
    listing_id: int


class SalesAnalyticResponse(SalesAnalyticBase):
    id: int
    listing_id: int
    sale_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="Flippify API",
    description="A tool for flipping products on eBay and Amazon efficiently",
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
@app.on_event("startup")
async def startup_event():
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


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Flippify API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Product endpoints
@app.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    source_platform: Optional[str] = None,
    target_platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if source_platform:
        query = query.filter(Product.source_platform == source_platform)
    if target_platform:
        query = query.filter(Product.target_platform == target_platform)
    
    products = query.offset(skip).limit(limit).all()
    return products


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == product.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if SKU already exists
    if product.sku:
        existing_product = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{id}", response_model=ProductResponse)
def update_product(id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.model_dump(exclude_unset=True)
    
    # Check if SKU is being updated and if it already exists
    if "sku" in update_data and update_data["sku"]:
        existing_product = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != id
        ).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{id}", status_code=204)
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete associated listings and pricing rules
    db.query(Listing).filter(Listing.product_id == id).delete()
    db.query(PricingRule).filter(PricingRule.product_id == id).delete()
    
    db.delete(product)
    db.commit()
    return None


# Listing endpoints
@app.get("/listings", response_model=List[ListingResponse])
def get_listings(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Listing)
    
    if platform:
        query = query.filter(Listing.platform == platform)
    if status:
        query = query.filter(Listing.status == status)
    if product_id:
        query = query.filter(Listing.product_id == product_id)
    
    listings = query.offset(skip).limit(limit).all()
    return listings


@app.post("/listings", response_model=ListingResponse, status_code=201)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == listing.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == listing.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if listing_id already exists
    if listing.listing_id:
        existing_listing = db.query(Listing).filter(Listing.listing_id == listing.listing_id).first()
        if existing_listing:
            raise HTTPException(status_code=400, detail="Listing with this ID already exists")
    
    db_listing = Listing(**listing.model_dump())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


@app.get("/listings/{id}", response_model=ListingResponse)
def get_listing(id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@app.put("/listings/{id}", response_model=ListingResponse)
def update_listing(id: int, listing_update: ListingUpdate, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    update_data = listing_update.model_dump(exclude_unset=True)
    
    # Check if listing_id is being updated and if it already exists
    if "listing_id" in update_data and update_data["listing_id"]:
        existing_listing = db.query(Listing).filter(
            Listing.listing_id == update_data["listing_id"],
            Listing.id != id
        ).first()
        if existing_listing:
            raise HTTPException(status_code=400, detail="Listing with this ID already exists")
    
    for key, value in update_data.items():
        setattr(listing, key, value)
    
    listing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(listing)
    return listing


@app.delete("/listings/{id}", status_code=204)
def delete_listing(id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Delete associated sales analytics
    db.query(SalesAnalytic).filter(SalesAnalytic.listing_id == id).delete()
    
    db.delete(listing)
    db.commit()
    return None


# Pricing Rules endpoints
@app.get("/pricing-rules", response_model=List[PricingRuleResponse])
def get_pricing_rules(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PricingRule)
    
    if product_id:
        query = query.filter(PricingRule.product_id == product_id)
    
    rules = query.offset(skip).limit(limit).all()
    return rules


@app.post("/pricing-rules", response_model=PricingRuleResponse, status_code=201)
def create_pricing_rule(rule: PricingRuleCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == rule.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_rule = PricingRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@app.get("/pricing-rules/{id}", response_model=PricingRuleResponse)
def get_pricing_rule(id: int, db: Session = Depends(get_db)):
    rule = db.query(PricingRule).filter(PricingRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    return rule


@app.delete("/pricing-rules/{id}", status_code=204)
def delete_pricing_rule(id: int, db: Session = Depends(get_db)):
    rule = db.query(PricingRule).filter(PricingRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    db.delete(rule)
    db.commit()
    return None


# Sales Analytics endpoints
@app.get("/sales-analytics", response_model=List[SalesAnalyticResponse])
def get_sales_analytics(
    skip: int = 0,
    limit: int = 100,
    listing_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SalesAnalytic)
    
    if listing_id:
        query = query.filter(SalesAnalytic.listing_id == listing_id)
    
    analytics = query.offset(skip).limit(limit).all()
    return analytics


@app.post("/sales-analytics", response_model=SalesAnalyticResponse, status_code=201)
def create_sales_analytic(analytic: SalesAnalyticCreate, db: Session = Depends(get_db)):
    # Check if listing exists
    listing = db.query(Listing).filter(Listing.id == analytic.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    db_analytic = SalesAnalytic(**analytic.model_dump())
    db.add(db_analytic)
    db.commit()
    db.refresh(db_analytic)
    return db_analytic


@app.get("/sales-analytics/{id}", response_model=SalesAnalyticResponse)
def get_sales_analytic(id: int, db: Session = Depends(get_db)):
    analytic = db.query(SalesAnalytic).filter(SalesAnalytic.id == id).first()
    if not analytic:
        raise HTTPException(status_code=404, detail="Sales analytic not found")
    return analytic


# Dashboard summary endpoint
@app.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_products = db.query(Product).count()
    total_listings = db.query(Listing).count()
    active_listings = db.query(Listing).filter(Listing.status == "active").count()
    total_sales = db.query(SalesAnalytic).count()
    
    total_revenue = db.query(SalesAnalytic).with_entities(
        db.func.sum(SalesAnalytic.sale_price * SalesAnalytic.quantity_sold)
    ).scalar() or 0.0
    
    total_profit = db.query(SalesAnalytic).with_entities(
        db.func.sum(SalesAnalytic.profit)
    ).scalar() or 0.0
    
    return {
        "total_products": total_products,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_sales": total_sales,
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2)
    }


# Inventory sync endpoint
@app.post("/inventory/sync")
def sync_inventory(db: Session = Depends(get_db)):
    """
    Synchronize inventory between products and listings.
    Updates listing quantities based on product quantities.
    """
    products = db.query(Product).all()
    synced_count = 0
    
    for product in products:
        listings = db.query(Listing).filter(
            Listing.product_id == product.id,
            Listing.status == "active"
        ).all()
        
        for listing in listings:
            if listing.quantity != product.quantity:
                listing.quantity = product.quantity
                listing.updated_at = datetime.utcnow()
                synced_count += 1
    
    db.commit()
    
    return {
        "message": "Inventory synchronized successfully",
        "synced_listings": synced_count
    }


# Dynamic repricing endpoint
@app.post("/repricing/apply/{product_id}")
def apply_repricing(product_id: int, db: Session = Depends(get_db)):
    """
    Apply pricing rules to a product's listings.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    pricing_rules = db.query(PricingRule).filter(
        PricingRule.product_id == product_id,
        PricingRule.auto_reprice == True
    ).all()
    
    if not pricing_rules:
        raise HTTPException(status_code=404, detail="No auto-repricing rules found for this product")
    
    listings = db.query(Listing).filter(
        Listing.product_id == product_id,
        Listing.status == "active"
    ).all()
    
    repriced_count = 0
    
    for listing in listings:
        for rule in pricing_rules:
            # Calculate new price
            new_price = product.source_price
            new_price += (new_price * rule.markup_percentage / 100)
            new_price += rule.markup_fixed
            
            # Apply min/max constraints
            if rule.min_price and new_price < rule.min_price:
                new_price = rule.min_price
            if rule.max_price and new_price > rule.max_price:
                new_price = rule.max_price
            
            if listing.price != new_price:
                listing.price = round(new_price, 2)
                listing.updated_at = datetime.utcnow()
                repriced_count += 1
    
    db.commit()
    
    return {
        "message": "Repricing applied successfully",
        "repriced_listings": repriced_count
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)