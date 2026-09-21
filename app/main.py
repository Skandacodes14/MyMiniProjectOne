from fastapi import FastAPI
import uvicorn

from app.DataBaseConnectionInfra import engine, Base
from app.Routers import (
    AuthenticationRouter,
    BookRouter,
    LoanRouter
)

# 1. Initialize DB tables
Base.metadata.create_all(bind=engine)

# 2. Instantiate main app
app = FastAPI(
    title="Library Management System",
    description="Production-ready REST API for book borrowing, member management, and queue reservations.",
    version="1.0.0",
)

# 3. Mount modular routers
app.include_router(AuthenticationRouter.router)
app.include_router(BookRouter.router)
app.include_router(LoanRouter.router)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "message": "Welcome to the Library Management System API. Visit /docs for Swagger documentation."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)