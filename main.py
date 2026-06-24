from fastapi import FastAPI, Query, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional

DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(title="Product API")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    category = Column(String(100))
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "message": "Product API is running!",
        "endpoints": {
            "/products": "Browse products with pagination",
            "/products/cursor": "Browse with cursor pagination (recommended)",
            "/categories": "Get all categories",
            "/docs": "Interactive API documentation"
        }
    }

@app.get("/products")
def get_products(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    total_count = query.count()
    offset = (page - 1) * limit
    
    products = query.order_by(desc(Product.created_at), desc(Product.id)).offset(offset).limit(limit).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in products
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit
        }
    }

@app.get("/products/cursor")
def get_products_cursor(
    category: Optional[str] = None,
    cursor: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    if cursor:
        query = query.filter(Product.id < cursor)
    
    products = query.order_by(desc(Product.created_at), desc(Product.id)).limit(limit + 1).all()
    
    has_more = len(products) > limit
    products = products[:limit]
    
    next_cursor = products[-1].id if products else None
    
    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in products
        ],
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more,
            "limit": limit
        }
    }

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Product.category).distinct().all()
    return {
        "success": True,
        "categories": [c[0] for c in categories]
    }