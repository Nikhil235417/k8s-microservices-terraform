from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import create_engine, text

app = FastAPI(title="Users Service", description="Service for managing users")

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
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """))
        conn.execute(text("""
            INSERT INTO users (name)
            SELECT 'Roberto' WHERE NOT EXISTS (SELECT 1 FROM users WHERE name = 'Roberto')
        """))
        conn.execute(text("""
            INSERT INTO users (name)
            SELECT 'Alicia' WHERE NOT EXISTS (SELECT 1 FROM users WHERE name = 'Alicia')
        """))
        conn.commit()
            
@app.get("/")
def read_root():
    return {"service": "users-service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/users")
def get_users():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name FROM users"))
            users = [{"id": row[0], "name": row[1]} for row in result]
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")