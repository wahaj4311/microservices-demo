from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import redis
from typing import List, Optional

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL)

app = FastAPI(title="Product Service", description="Product Catalog and Inventory Management")

# Database Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer)
    category = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# Pydantic models
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cache decorator
def cache_response(expire_time=300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return eval(cached_result)
            
            # If not in cache, execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, expire_time, str(result))
            return result
        return wrapper
    return decorator

@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Invalidate cache
    redis_client.delete("get_products")
    return db_product

@app.get("/products/", response_model=List[ProductResponse])
@cache_response(expire_time=300)
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
@cache_response(expire_time=300)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    
    # Invalidate cache
    redis_client.delete(f"get_product:{product_id}")
    redis_client.delete("get_products")
    return db_product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    
    # Invalidate cache
    redis_client.delete(f"get_product:{product_id}")
    redis_client.delete("get_products")
    return {"message": "Product deleted"}

@app.put("/products/{product_id}/stock")
async def update_stock(product_id: int, stock_change: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_stock = db_product.stock + stock_change
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    db_product.stock = new_stock
    db.commit()
    
    # Invalidate cache
    redis_client.delete(f"get_product:{product_id}")
    redis_client.delete("get_products")
    return {"message": "Stock updated", "new_stock": new_stock}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
