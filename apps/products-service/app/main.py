import os
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import create_engine, text

app = FastAPI(title="Products Service", description="Service for managing products")

Instrumentator().instrument(app).expose(app)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", 5432)   
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")    
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.on_event("startup")
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price NUMERIC(10, 2) NOT NULL
            )
        """))
        conn.execute(text("""
            INSERT INTO products (name, price)
            SELECT 'Laptop', 1200.00 WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Laptop')
        """))
        conn.execute(text("""
            INSERT INTO products (name, price)
            SELECT 'Mouse', 800.00 WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Smartphone')
        """))
        conn.commit()

@app.get("/")
def read_root():
    return {"service": "products-service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/products")
def get_products():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, price FROM products"))
            products = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in result]
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")