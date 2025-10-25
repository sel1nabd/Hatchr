import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel, Field
from contextlib import contextmanager

# Database setup
DATABASE_URL = "sqlite:///./markdown_notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
note_tags = Table(
    'note_tags',
    Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('note_id', Integer, ForeignKey('notes.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    notes = relationship("Note", secondary=note_tags, back_populates="tags")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    
    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")

class NoteCreate(NoteBase):
    tag_ids: List[int] = Field(default_factory=list)

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

class NoteListResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(
    title="Markdown Notes API",
    description="A simple note-taking app with markdown support",
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

# Database dependency
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Markdown Notes API",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Notes Endpoints
@app.get("/notes", response_model=List[NoteListResponse])
def get_notes(
    search: Optional[str] = Query(None, description="Search in title and content"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all notes with optional search and tag filtering"""
    with get_db() as db:
        query = db.query(Note)
        
        # Search functionality
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Note.title.ilike(search_term),
                    Note.content.ilike(search_term)
                )
            )
        
        # Tag filtering
        if tag:
            query = query.join(Note.tags).filter(Tag.name == tag)
        
        notes = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
        return notes

@app.post("/notes", response_model=NoteResponse, status_code=201)
def create_note(note: NoteCreate):
    """Create a new note"""
    with get_db() as db:
        # Verify tags exist
        if note.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(note.tag_ids)).all()
            if len(tags) != len(note.tag_ids):
                raise HTTPException(status_code=400, detail="One or more tag IDs are invalid")
        else:
            tags = []
        
        # Create note
        db_note = Note(
            title=note.title,
            content=note.content,
            tags=tags
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int):
    """Get a specific note by ID"""
    with get_db() as db:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_update: NoteUpdate):
    """Update a note"""
    with get_db() as db:
        db_note = db.query(Note).filter(Note.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Update fields
        if note_update.title is not None:
            db_note.title = note_update.title
        if note_update.content is not None:
            db_note.content = note_update.content
        
        # Update tags if provided
        if note_update.tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(note_update.tag_ids)).all()
            if len(tags) != len(note_update.tag_ids):
                raise HTTPException(status_code=400, detail="One or more tag IDs are invalid")
            db_note.tags = tags
        
        db_note.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_note)
        return db_note

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    """Delete a note"""
    with get_db() as db:
        db_note = db.query(Note).filter(Note.id == note_id).first()
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        db.delete(db_note)
        db.commit()
        return None

# Tags Endpoints
@app.get("/tags", response_model=List[TagResponse])
def get_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all tags"""
    with get_db() as db:
        tags = db.query(Tag).order_by(Tag.name).offset(skip).limit(limit).all()
        return tags

@app.post("/tags", response_model=TagResponse, status_code=201)
def create_tag(tag: TagCreate):
    """Create a new tag"""
    with get_db() as db:
        # Check if tag already exists
        existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
        if existing_tag:
            raise HTTPException(status_code=400, detail="Tag with this name already exists")
        
        db_tag = Tag(name=tag.name)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

@app.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int):
    """Get a specific tag by ID"""
    with get_db() as db:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag

@app.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag_update: TagUpdate):
    """Update a tag"""
    with get_db() as db:
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not db_tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        # Check if new name conflicts with existing tag
        existing_tag = db.query(Tag).filter(Tag.name == tag_update.name, Tag.id != tag_id).first()
        if existing_tag:
            raise HTTPException(status_code=400, detail="Tag with this name already exists")
        
        db_tag.name = tag_update.name
        db.commit()
        db.refresh(db_tag)
        return db_tag

@app.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int):
    """Delete a tag"""
    with get_db() as db:
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not db_tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        db.delete(db_tag)
        db.commit()
        return None

# Search endpoint (additional feature)
@app.get("/search", response_model=List[NoteListResponse])
def search_notes(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search notes by title or content"""
    with get_db() as db:
        search_term = f"%{q}%"
        notes = db.query(Note).filter(
            or_(
                Note.title.ilike(search_term),
                Note.content.ilike(search_term)
            )
        ).order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
        return notes

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)