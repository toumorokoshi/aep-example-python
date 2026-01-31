from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import init_db
from api import router
import uvicorn
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    lifespan=lifespan,
    title="Library API",
    version="1.0.0",
    description="A simple library API.",
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local server"}
    ]
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
