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
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="user")
    sales = relationship("Sale", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    source_platform = Column(String)  # Where product was sourced from
    source_url = Column(String)
    source_price = Column(Float, nullable=False)
    target_platform = Column(String)  # eBay or Amazon
    target_price = Column(Float)
    current_price = Column(Float)
    category = Column(String)
    sku = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=1)
    status = Column(String, default="active")  # active, sold, delisted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="product")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    platform = Column(String)  # eBay or Amazon
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    product = relationship("Product", back_populates="price_history")

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sale_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    platform = Column(String)  # eBay or Amazon
    fees = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    net_profit = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow, index=True)
    order_id = Column(String, unique=True)
    notes = Column(Text)
    
    user = relationship("User", back_populates="sales")
    product = relationship("Product", back_populates="sales")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    alert_type = Column(String, nullable=False)  # price_drop, price_increase, stock_alert
    condition = Column(String)  # JSON string with condition details
    threshold_value = Column(Float)
    is_active = Column(Boolean, default=True)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="alerts")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    source_price: float
    target_platform: Optional[str] = None
    target_price: Optional[float] = None
    current_price: Optional[float] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: int = 1
    status: str = "active"

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    source_price: Optional[float] = None
    target_platform: Optional[str] = None
    target_price: Optional[float] = None
    current_price: Optional[float] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    source_platform: Optional[str]
    source_url: Optional[str]
    source_price: float
    target_platform: Optional[str]
    target_price: Optional[float]
    current_price: Optional[float]
    category: Optional[str]
    sku: Optional[str]
    quantity: int
    status: str
    profit_margin: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PriceHistoryCreate(BaseModel):
    product_id: int
    price: float
    platform: Optional[str] = None

class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    platform: Optional[str]
    recorded_at: datetime
    
    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    user_id: int
    product_id: int
    sale_price: float
    cost_price: float
    platform: Optional[str] = None
    fees: float = 0.0
    shipping_cost: float = 0.0
    order_id: Optional[str] = None
    notes: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    sale_price: float
    cost_price: float
    profit: float
    platform: Optional[str]
    fees: float
    shipping_cost: float
    net_profit: float
    sale_date: datetime
    order_id: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    user_id: int
    product_id: Optional[int] = None
    alert_type: str
    condition: Optional[str] = None
    threshold_value: Optional[float] = None
    message: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    user_id: int
    product_id: Optional[int]
    alert_type: str
    condition: Optional[str]
    threshold_value: Optional[float]
    is_active: bool
    message: Optional[str]
    created_at: datetime
    triggered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SalesAnalytics(BaseModel):
    total_sales: int
    total_revenue: float
    total_profit: float
    total_net_profit: float
    average_profit_margin: float
    total_fees: float
    total_shipping_cost: float

# FastAPI app
app = FastAPI(
    title="Flippify API",
    description="A platform for flipping products on eBay and Amazon",
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

# Helper function to calculate profit margin
def calculate_profit_margin(source_price: float, target_price: Optional[float]) -> Optional[float]:
    if target_price and source_price > 0:
        return ((target_price - source_price) / source_price) * 100
    return None

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
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Product endpoints
@app.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if user_id:
        query = query.filter(Product.user_id == user_id)
    if status:
        query = query.filter(Product.status == status)
    if category:
        query = query.filter(Product.category == category)
    
    products = query.offset(skip).limit(limit).all()
    
    # Add profit margin calculation
    result = []
    for product in products:
        product_dict = ProductResponse.from_orm(product).dict()
        product_dict["profit_margin"] = calculate_profit_margin(
            product.source_price,
            product.target_price
        )
        result.append(ProductResponse(**product_dict))
    
    return result

@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == product.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if SKU already exists
    if product.sku:
        existing_product = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Create initial price history entry
    if new_product.current_price:
        price_history = PriceHistory(
            product_id=new_product.id,
            price=new_product.current_price,
            platform=new_product.target_platform
        )
        db.add(price_history)
        db.commit()
    
    product_dict = ProductResponse.from_orm(new_product).dict()
    product_dict["profit_margin"] = calculate_profit_margin(
        new_product.source_price,
        new_product.target_price
    )
    
    return ProductResponse(**product_dict)

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_dict = ProductResponse.from_orm(product).dict()
    product_dict["profit_margin"] = calculate_profit_margin(
        product.source_price,
        product.target_price
    )
    
    return ProductResponse(**product_dict)

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    
    # Track price changes
    if "current_price" in update_data and update_data["current_price"] != product.current_price:
        price_history = PriceHistory(
            product_id=product.id,
            price=update_data["current_price"],
            platform=product.target_platform
        )
        db.add(price_history)
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    product_dict = ProductResponse.from_orm(product).dict()
    product_dict["profit_margin"] = calculate_profit_margin(
        product.source_price,
        product.target_price
    )
    
    return ProductResponse(**product_dict)

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return None

# Price History endpoints
@app.get("/price-history/{product_id}", response_model=List[PriceHistoryResponse])
def get_price_history(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    price_history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).order_by(PriceHistory.recorded_at.desc()).offset(skip).limit(limit).all()
    
    return price_history

@app.post("/price-history", response_model=PriceHistoryResponse, status_code=201)
def create_price_history(price_history: PriceHistoryCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == price_history.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_price_history = PriceHistory(**price_history.dict())
    db.add(new_price_history)
    
    # Update product's current price
    product.current_price = price_history.price
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_price_history)
    
    return new_price_history

# Sales endpoints
@app.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    product_id: Optional[int] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Sale)
    
    if user_id:
        query = query.filter(Sale.user_id == user_id)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if platform:
        query = query.filter(Sale.platform == platform)
    
    sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    return sales

@app.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == sale.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == sale.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate profit and net profit
    profit = sale.sale_price - sale.cost_price
    net_profit = profit - sale.fees - sale.shipping_cost
    
    new_sale = Sale(
        user_id=sale.user_id,
        product_id=sale.product_id,
        sale_price=sale.sale_price,
        cost_price=sale.cost_price,
        profit=profit,
        platform=sale.platform,
        fees=sale.fees,
        shipping_cost=sale.shipping_cost,
        net_profit=net_profit,
        order_id=sale.order_id,
        notes=sale.notes
    )
    
    db.add(new_sale)
    
    # Update product status and quantity
    product.quantity -= 1
    if product.quantity <= 0:
        product.status = "sold"
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_sale)
    
    return new_sale

@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@app.get("/sales/analytics/summary", response_model=SalesAnalytics)
def get_sales_analytics(
    user_id: Optional[int] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Sale)
    
    if user_id:
        query = query.filter(Sale.user_id == user_id)
    if platform:
        query = query.filter(Sale.platform == platform)
    
    sales = query.all()
    
    if not sales:
        return SalesAnalytics(
            total_sales=0,
            total_revenue=0.0,
            total_profit=0.0,
            total_net_profit=0.0,
            average_profit_margin=0.0,
            total_fees=0.0,
            total_shipping_cost=0.0
        )
    
    total_sales = len(sales)
    total_revenue = sum(sale.sale_price for sale in sales)
    total_profit = sum(sale.profit for sale in sales)
    total_net_profit = sum(sale.net_profit for sale in sales)
    total_fees = sum(sale.fees for sale in sales)
    total_shipping_cost = sum(sale.shipping_cost for sale in sales)
    
    # Calculate average profit margin
    total_cost = sum(sale.cost_price for sale in sales)
    average_profit_margin = (total_profit / total_cost * 100) if total_cost > 0 else 0.0
    
    return SalesAnalytics(
        total_sales=total_sales,
        total_revenue=total_revenue,
        total_profit=total_profit,
        total_net_profit=total_net_profit,
        average_profit_margin=round(average_profit_margin, 2),
        total_fees=total_fees,
        total_shipping_cost=total_shipping_cost
    )

# Alert endpoints
@app.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    
    if user_id:
        query = query.filter(Alert.user_id == user_id)
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@app.post("/alerts", response_model=AlertResponse, status_code=201)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == alert.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify product exists if product_id is provided
    if alert.product_id:
        product = db.query(Product).filter(Product.id == alert.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    new_alert = Alert(**alert.dict())
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    return new_alert

@app.get("/alerts/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.put("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: int, is_active: bool, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = is_active
    db.commit()
    db.refresh(alert)
    
    return alert

@app.delete("/alerts/{alert_id}", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return None

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)