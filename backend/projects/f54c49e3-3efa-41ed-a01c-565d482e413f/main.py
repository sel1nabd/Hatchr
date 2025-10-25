import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field

# Database setup
DATABASE_URL = "sqlite:///./kickstart_africa.db"
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
    
    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(String, default="football")
    durability_rating = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")


class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="inventory")


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock: int = Field(ge=0, description="Stock must be non-negative")
    category: str = "football"
    durability_rating: int = Field(ge=1, le=10, default=5)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    durability_rating: Optional[int] = Field(None, ge=1, le=10)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: int
    total_price: float
    order_date: datetime
    status: str
    
    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity_available: int
    last_updated: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="KickStart Africa API",
    description="An online platform to sell affordable, durable footballs for kids in Africa",
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


# Initialize sample data
def init_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Product).count() > 0:
            return
        
        # Create sample users
        users = [
            User(name="John Doe", email="john@example.com"),
            User(name="Jane Smith", email="jane@example.com"),
            User(name="Ahmed Hassan", email="ahmed@example.com"),
        ]
        db.add_all(users)
        db.commit()
        
        # Create sample products
        products = [
            Product(
                name="KickStart Classic Football",
                description="Durable, affordable football perfect for African youth. Made with high-quality synthetic leather.",
                price=15.99,
                stock=100,
                durability_rating=8
            ),
            Product(
                name="KickStart Pro Football",
                description="Professional-grade football with enhanced durability. Ideal for regular training and matches.",
                price=24.99,
                stock=75,
                durability_rating=9
            ),
            Product(
                name="KickStart Junior Football",
                description="Lightweight football designed for younger children. Easy to control and highly durable.",
                price=12.99,
                stock=150,
                durability_rating=7
            ),
            Product(
                name="KickStart All-Weather Football",
                description="Specially designed to withstand all weather conditions. Perfect for year-round play.",
                price=19.99,
                stock=80,
                durability_rating=10
            ),
            Product(
                name="KickStart Community Pack (5 Balls)",
                description="Bulk pack of 5 durable footballs at a discounted price. Perfect for schools and community centers.",
                price=69.99,
                stock=30,
                durability_rating=8
            ),
        ]
        db.add_all(products)
        db.commit()
        
        # Create inventory entries for each product
        for product in products:
            inventory = Inventory(product_id=product.id, quantity_available=product.stock)
            db.add(inventory)
        
        db.commit()
    finally:
        db.close()


# Initialize data on startup
@app.on_event("startup")
def startup_event():
    init_sample_data()


# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to KickStart Africa API",
        "description": "Affordable, durable footballs for kids in Africa",
        "docs": "/docs",
        "endpoints": {
            "products": "/products",
            "orders": "/orders",
            "users": "/users",
            "inventory": "/inventory"
        }
    }


# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "database": "connected"}


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Product endpoints
@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_products(
    skip: int = 0,
    limit: int = 100,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all products with optional filters"""
    query = db.query(Product)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock is not None and in_stock:
        query = query.filter(Product.stock > 0)
    
    products = query.offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=ProductResponse, status_code=201, tags=["Products"])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Create inventory entry
    inventory = Inventory(product_id=new_product.id, quantity_available=new_product.stock)
    db.add(inventory)
    db.commit()
    
    return new_product


@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Update inventory if stock changed
    if "stock" in update_data:
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if inventory:
            inventory.quantity_available = update_data["stock"]
            inventory.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=204, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete associated inventory
    db.query(Inventory).filter(Inventory.product_id == product_id).delete()
    
    db.delete(db_product)
    db.commit()
    return None


# Order endpoints
@app.post("/orders", response_model=OrderResponse, status_code=201, tags=["Orders"])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Verify user exists
    user = db.query(User).filter(User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check stock availability
    if product.stock < order.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {product.stock}, Requested: {order.quantity}"
        )
    
    # Calculate total price
    total_price = product.price * order.quantity
    
    # Create order
    new_order = Order(
        user_id=order.user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        status="confirmed"
    )
    db.add(new_order)
    
    # Update product stock
    product.stock -= order.quantity
    
    # Update inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == order.product_id).first()
    if inventory:
        inventory.quantity_available -= order.quantity
        inventory.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(new_order)
    return new_order


@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all orders with optional filters"""
    query = db.query(Order)
    
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    if status is not None:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """Update order status"""
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return order


# Inventory endpoints
@app.get("/inventory", response_model=List[InventoryResponse], tags=["Inventory"])
def get_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all inventory records"""
    inventory = db.query(Inventory).offset(skip).limit(limit).all()
    return inventory


@app.get("/inventory/{product_id}", response_model=InventoryResponse, tags=["Inventory"])
def get_product_inventory(product_id: int, db: Session = Depends(get_db)):
    """Get inventory for a specific product"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return inventory


@app.put("/inventory/{product_id}", response_model=InventoryResponse, tags=["Inventory"])
def update_inventory(product_id: int, quantity: int, db: Session = Depends(get_db)):
    """Update inventory quantity for a product"""
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    inventory.quantity_available = quantity
    inventory.last_updated = datetime.utcnow()
    
    # Also update product stock
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.stock = quantity
    
    db.commit()
    db.refresh(inventory)
    return inventory


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)