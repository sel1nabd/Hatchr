import os
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, HttpUrl

# Database setup
DATABASE_URL = "sqlite:///./asdf_hub.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables
content_tags = Table(
    'content_tags',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content_items.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

feed_items = Table(
    'feed_items',
    Base.metadata,
    Column('feed_id', Integer, ForeignKey('feeds.id', ondelete='CASCADE'), primary_key=True),
    Column('content_id', Integer, ForeignKey('content_items.id', ondelete='CASCADE'), primary_key=True)
)

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    content_items = relationship("ContentItem", back_populates="user", cascade="all, delete-orphan")
    feeds = relationship("Feed", back_populates="user", cascade="all, delete-orphan")

class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="content_items")
    tags = relationship("Tag", secondary=content_tags, back_populates="content_items")
    feeds = relationship("Feed", secondary=feed_items, back_populates="content_items")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    content_items = relationship("ContentItem", secondary=content_tags, back_populates="tags")

class Feed(Base):
    __tablename__ = "feeds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="feeds")
    content_items = relationship("ContentItem", secondary=feed_items, back_populates="feeds")

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
    created_at: datetime
    
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContentItemBase(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    user_id: int

class ContentItemCreate(ContentItemBase):
    tag_names: Optional[List[str]] = []

class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    tag_names: Optional[List[str]] = None

class ContentItemResponse(ContentItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

class FeedBase(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: int

class FeedCreate(FeedBase):
    content_item_ids: Optional[List[int]] = []

class FeedUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content_item_ids: Optional[List[int]] = None

class FeedResponse(FeedBase):
    id: int
    created_at: datetime
    updated_at: datetime
    content_items: List[ContentItemResponse] = []
    
    class Config:
        from_attributes = True

class ShareRequest(BaseModel):
    content_id: int
    platform: str

class ShareResponse(BaseModel):
    success: bool
    share_url: str
    platform: str

# FastAPI app
app = FastAPI(
    title="ASDF Hub API",
    description="A digital content curation platform for organizing and sharing ASDF-related content",
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

# Helper functions
def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    tag = db.query(Tag).filter(Tag.name == tag_name.lower().strip()).first()
    if not tag:
        tag = Tag(name=tag_name.lower().strip())
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to ASDF Hub API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(name=user.name, email=user.email)
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

# Content Item endpoints
@app.get("/content-items", response_model=List[ContentItemResponse])
def get_content_items(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContentItem)
    
    if user_id:
        query = query.filter(ContentItem.user_id == user_id)
    
    if tag:
        query = query.join(ContentItem.tags).filter(Tag.name == tag.lower())
    
    content_items = query.offset(skip).limit(limit).all()
    return content_items

@app.post("/content-items", response_model=ContentItemResponse, status_code=201)
def create_content_item(content: ContentItemCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == content.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_content = ContentItem(
        title=content.title,
        url=content.url,
        description=content.description,
        user_id=content.user_id
    )
    
    # Add tags
    if content.tag_names:
        for tag_name in content.tag_names:
            tag = get_or_create_tag(db, tag_name)
            new_content.tags.append(tag)
    
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

@app.get("/content-items/{content_id}", response_model=ContentItemResponse)
def get_content_item(content_id: int, db: Session = Depends(get_db)):
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")
    return content

@app.put("/content-items/{content_id}", response_model=ContentItemResponse)
def update_content_item(
    content_id: int,
    content_update: ContentItemUpdate,
    db: Session = Depends(get_db)
):
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    if content_update.title is not None:
        content.title = content_update.title
    if content_update.url is not None:
        content.url = content_update.url
    if content_update.description is not None:
        content.description = content_update.description
    
    if content_update.tag_names is not None:
        content.tags.clear()
        for tag_name in content_update.tag_names:
            tag = get_or_create_tag(db, tag_name)
            content.tags.append(tag)
    
    content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content)
    return content

@app.delete("/content-items/{content_id}", status_code=204)
def delete_content_item(content_id: int, db: Session = Depends(get_db)):
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    db.delete(content)
    db.commit()
    return None

# Feed endpoints
@app.get("/feeds", response_model=List[FeedResponse])
def get_feeds(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Feed)
    
    if user_id:
        query = query.filter(Feed.user_id == user_id)
    
    feeds = query.offset(skip).limit(limit).all()
    return feeds

@app.post("/feeds", response_model=FeedResponse, status_code=201)
def create_feed(feed: FeedCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == feed.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_feed = Feed(
        name=feed.name,
        description=feed.description,
        user_id=feed.user_id
    )
    
    # Add content items
    if feed.content_item_ids:
        for content_id in feed.content_item_ids:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if content:
                new_feed.content_items.append(content)
    
    db.add(new_feed)
    db.commit()
    db.refresh(new_feed)
    return new_feed

@app.get("/feeds/{feed_id}", response_model=FeedResponse)
def get_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    return feed

@app.put("/feeds/{feed_id}", response_model=FeedResponse)
def update_feed(
    feed_id: int,
    feed_update: FeedUpdate,
    db: Session = Depends(get_db)
):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    if feed_update.name is not None:
        feed.name = feed_update.name
    if feed_update.description is not None:
        feed.description = feed_update.description
    
    if feed_update.content_item_ids is not None:
        feed.content_items.clear()
        for content_id in feed_update.content_item_ids:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if content:
                feed.content_items.append(content)
    
    feed.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(feed)
    return feed

@app.delete("/feeds/{feed_id}", status_code=204)
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    db.delete(feed)
    db.commit()
    return None

# Tag endpoints
@app.get("/tags", response_model=List[TagResponse])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return tags

@app.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

# Social sharing endpoint
@app.post("/share", response_model=ShareResponse)
def share_content(share_request: ShareRequest, db: Session = Depends(get_db)):
    content = db.query(ContentItem).filter(ContentItem.id == share_request.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    platform = share_request.platform.lower()
    base_url = content.url
    title = content.title
    
    share_urls = {
        "twitter": f"https://twitter.com/intent/tweet?url={base_url}&text={title}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={base_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={base_url}",
        "reddit": f"https://reddit.com/submit?url={base_url}&title={title}",
        "email": f"mailto:?subject={title}&body={base_url}"
    }
    
    if platform not in share_urls:
        raise HTTPException(status_code=400, detail=f"Unsupported platform. Supported: {', '.join(share_urls.keys())}")
    
    return ShareResponse(
        success=True,
        share_url=share_urls[platform],
        platform=platform
    )

# Bookmark endpoint (add content to feed)
@app.post("/feeds/{feed_id}/bookmark/{content_id}", response_model=FeedResponse)
def bookmark_content(feed_id: int, content_id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    if content not in feed.content_items:
        feed.content_items.append(content)
        feed.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(feed)
    
    return feed

# Remove bookmark
@app.delete("/feeds/{feed_id}/bookmark/{content_id}", response_model=FeedResponse)
def remove_bookmark(feed_id: int, content_id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    if content in feed.content_items:
        feed.content_items.remove(content)
        feed.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(feed)
    
    return feed

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)