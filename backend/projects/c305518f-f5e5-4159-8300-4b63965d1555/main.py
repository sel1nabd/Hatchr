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
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    
    items = relationship("Item", back_populates="owner", foreign_keys="Item.user_id")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")
    purchases = relationship("Transaction", back_populates="buyer", foreign_keys="Transaction.buyer_id")
    sales = relationship("Transaction", back_populates="seller", foreign_keys="Transaction.seller_id")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    items = relationship("Item", back_populates="category_rel")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    status = Column(String, default="available", index=True)  # available, sold, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="items", foreign_keys=[user_id])
    category_rel = relationship("Category", back_populates="items")
    messages = relationship("Message", back_populates="item")
    transactions = relationship("Transaction", back_populates="item")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_messages", foreign_keys=[receiver_id])
    item = relationship("Item", back_populates="messages")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, cancelled
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    item = relationship("Item", back_populates="transactions")
    buyer = relationship("User", back_populates="purchases", foreign_keys=[buyer_id])
    seller = relationship("User", back_populates="sales", foreign_keys=[seller_id])


# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
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


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    category_id: Optional[int] = None


class ItemCreate(ItemBase):
    user_id: int


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    status: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    sender_id: int
    receiver_id: int
    item_id: int


class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    item_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    item_id: int
    buyer_id: int
    price: float


class TransactionCreate(TransactionBase):
    seller_id: int


class TransactionResponse(TransactionBase):
    id: int
    seller_id: int
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# FastAPI app
app = FastAPI(
    title="Flippify API",
    description="A platform for buying and selling flipped items efficiently",
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
def init_default_categories(db: Session):
    default_categories = [
        "Electronics",
        "Clothing",
        "Home & Garden",
        "Sports & Outdoors",
        "Toys & Games",
        "Books",
        "Collectibles",
        "Furniture",
        "Other"
    ]
    
    for cat_name in default_categories:
        existing = db.query(Category).filter(Category.name == cat_name).first()
        if not existing:
            db.add(Category(name=cat_name))
    
    db.commit()


# Initialize database with default data
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        init_default_categories(db)
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


# User endpoints
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


# Category endpoints
@app.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Item endpoints
@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == item.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify category exists if provided
    if item.category_id:
        category = db.query(Category).filter(Category.id == item.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items", response_model=List[ItemResponse])
def get_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Item)
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if status:
        query = query.filter(Item.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Item.title.ilike(search_term)) | (Item.description.ilike(search_term))
        )
    
    if min_price is not None:
        query = query.filter(Item.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Item.price <= max_price)
    
    items = query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()
    return items


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    
    # Verify category exists if being updated
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate status if being updated
    if "status" in update_data:
        valid_statuses = ["available", "sold", "pending"]
        if update_data["status"] not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return None


# Message endpoints
@app.post("/messages", response_model=MessageResponse, status_code=201)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    # Verify sender exists
    sender = db.query(User).filter(User.id == message.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    # Verify receiver exists
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Verify item exists
    item = db.query(Item).filter(Item.id == message.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_message = Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get("/messages/{item_id}", response_model=List[MessageResponse])
def get_messages_by_item(item_id: int, db: Session = Depends(get_db)):
    # Verify item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    messages = db.query(Message).filter(Message.item_id == item_id).order_by(Message.timestamp.asc()).all()
    return messages


@app.get("/messages/user/{user_id}", response_model=List[MessageResponse])
def get_messages_by_user(user_id: int, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.timestamp.desc()).all()
    return messages


# Transaction endpoints
@app.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # Verify item exists
    item = db.query(Item).filter(Item.id == transaction.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if item is available
    if item.status != "available":
        raise HTTPException(status_code=400, detail="Item is not available for purchase")
    
    # Verify buyer exists
    buyer = db.query(User).filter(User.id == transaction.buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    # Verify seller exists
    seller = db.query(User).filter(User.id == transaction.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Buyer cannot be the seller
    if transaction.buyer_id == transaction.seller_id:
        raise HTTPException(status_code=400, detail="Buyer and seller cannot be the same user")
    
    # Create transaction
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    
    # Update item status to pending
    item.status = "pending"
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()
    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.put("/transactions/{transaction_id}/status", response_model=TransactionResponse)
def update_transaction_status(transaction_id: int, status: str, db: Session = Depends(get_db)):
    valid_statuses = ["pending", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = status
    
    # Update item status based on transaction status
    item = db.query(Item).filter(Item.id == transaction.item_id).first()
    if status == "completed":
        item.status = "sold"
    elif status == "cancelled":
        item.status = "available"
    
    db.commit()
    db.refresh(transaction)
    return transaction


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)