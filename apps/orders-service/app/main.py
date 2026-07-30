from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Orders Service", description="Service for managing orders")

Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    return {"service": "orders-service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/orders")
def get_orders():
    return {
        "orders": [
            {"id": 1, "item": "Laptop", "quantity": 2},
            {"id": 2, "item": "Smartphone", "quantity": 5}
        ]
    }