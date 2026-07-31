import os
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import create_engine, text

app = FastAPI(title="Orders Service", description="Service for managing orders")

Instrumentator().instrument(app).expose(app)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.on_event("startup")
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                total NUMERIC(10, 2) NOT NULL
            )
        """))
        conn.execute(text("""
            INSERT INTO orders (user_id, total)
            SELECT 1, 59.99 WHERE NOT EXISTS (SELECT 1 FROM orders WHERE user_id = 1)
        """))
        conn.execute(text("""
            INSERT INTO orders (user_id, total)
            SELECT 2, 120.50 WHERE NOT EXISTS (SELECT 1 FROM orders WHERE user_id = 2)
        """))
        conn.commit()

@app.get("/")
def read_root():
    return {"service": "orders-service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/orders")
def get_orders():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, user_id, total FROM orders"))
            orders = [{"id": r[0], "user_id": r[1], "total": float(r[2])} for r in result]
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")