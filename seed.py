from faker import Faker
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random
import time

DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    category = Column(String(100))
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def seed_database():
    Base.metadata.create_all(bind=engine)
    
    fake = Faker()
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Food', 'Automotive', 'Health', 'Beauty']
    
    batch_size = 1000
    total_products = 200000
    
    db = SessionLocal()
    
    print(f"Starting to seed {total_products:,} products...")
    start_time = time.time()
    
    for batch_num in range(0, total_products, batch_size):
        products = []
        current_batch_size = min(batch_size, total_products - batch_num)
        
        for _ in range(current_batch_size):
            product = Product(
                name=fake.catch_phrase(),
                category=random.choice(categories),
                price=round(random.uniform(5.99, 999.99), 2),
                created_at=fake.date_time_between(start_date='-2y', end_date='now'),
                updated_at=datetime.utcnow()
            )
            products.append(product)
        
        db.bulk_save_objects(products)
        db.commit()
        
        seeded = batch_num + current_batch_size
        print(f" Seeded {seeded:,} / {total_products:,} products ({seeded/total_products*100:.1f}%)")
    
    db.close()
    
    elapsed_time = time.time() - start_time
    print(f"\n Successfully seeded {total_products:,} products in {elapsed_time:.2f} seconds!")

if __name__ == "__main__":
    print(" Starting database seeding...")
    seed_database()
    print("\n Run API with: uvicorn main:app --reload")