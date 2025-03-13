from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
import enum
from datetime import datetime
from typing import List, Optional
import json

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Order Service", description="Order Processing and Management")

# Enums
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Database Models
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", backref="items")

Base.metadata.create_all(bind=engine)

# Pydantic models
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItemCreate]

class OrderItemResponse(OrderItemCreate):
    id: int
    price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: str
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_and_update_stock(items: List[OrderItemCreate]) -> float:
    async with httpx.AsyncClient() as client:
        total_amount = 0
        for item in items:
            # Get product details
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{item.product_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            product = response.json()
            if product["stock"] < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")
            
            # Update stock
            stock_response = await client.put(
                f"{PRODUCT_SERVICE_URL}/products/{item.product_id}/stock",
                json={"stock_change": -item.quantity}
            )
            if stock_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to update product stock")
            
            total_amount += product["price"] * item.quantity
            
        return total_amount

@app.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Verify products and update stock
    total_amount = await verify_and_update_stock(order.items)
    
    # Create order
    db_order = Order(
        user_id=order.user_id,
        total_amount=total_amount
    )
    db.add(db_order)
    db.flush()
    
    # Create order items
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=total_amount / len(order.items)  # Simplified price calculation
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"message": "Order status updated", "status": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
