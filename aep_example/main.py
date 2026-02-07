from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .db import init_db
from .api import router
import uvicorn

@asynccontextmanager
async def setup_db(app: FastAPI):
    # Startup: Create tables
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    lifespan=setup_db,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ui.aep.dev", "http://ui.aep.dev",
        # this is the standard port for aep-explorer locally.
        # so we should allow this for development purpose.
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

def start():
    uvicorn.run("aep_example.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
