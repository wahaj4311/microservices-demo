from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import redis
from typing import List, Optional
import json

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL)

app = FastAPI(title="Product Service", description="Product Catalog and Inventory Management")

@app.get("/health")
async def health_check():
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        # Check Redis connection
        redis_client.ping()
        
        return {"status": "healthy"}
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/ready")
async def readiness_check():
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        # Check Redis connection
        redis_client.ping()
        
        return {"status": "ready"}
    except Exception as e:
        print(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

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

class StockUpdate(BaseModel):
    stock_change: int

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def cache_response(expire_time=300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create a simpler cache key
            cache_key = f"{func.__name__}"
            if 'product_id' in kwargs:
                cache_key += f":{kwargs['product_id']}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # If not in cache, execute function
            result = await func(*args, **kwargs)
            
            # Convert to dict if it's a SQLAlchemy model
            if hasattr(result, '__dict__'):
                result_dict = dict(result.__dict__)
                if '_sa_instance_state' in result_dict:
                    del result_dict['_sa_instance_state']
                redis_client.setex(cache_key, expire_time, json.dumps(result_dict))
            else:
                # Handle list of products
                result_list = [dict(r.__dict__) for r in result]
                for r in result_list:
                    if '_sa_instance_state' in r:
                        del r['_sa_instance_state']
                redis_client.setex(cache_key, expire_time, json.dumps(result_list))
            
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
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
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
async def update_stock(product_id: int, stock_update: StockUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_stock = db_product.stock + stock_update.stock_change
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
