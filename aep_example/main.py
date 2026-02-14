from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .db import init_db
from .api import router

from .exceptions import http_exception_handler, validation_exception_handler
from .models import ProblemDetails
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


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
    ],
    exception_handlers={
        StarletteHTTPException: http_exception_handler,
        RequestValidationError: validation_exception_handler,
    },
    responses={
        422: {"model": ProblemDetails, "description": "Validation Error"},
        400: {"model": ProblemDetails, "description": "Bad Request"},
        404: {"model": ProblemDetails, "description": "Not Found"},
        500: {"model": ProblemDetails, "description": "Internal Server Error"},
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ui.aep.dev", "http://ui.aep.dev",
        # this is the standard port for aep-explorer locally.
        # so we should allow this for development purpose.
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

import argparse
import json
import uvicorn

def run_server():
    uvicorn.run("aep_example.main:app", host="0.0.0.0", port=8000, reload=True)

def generate_openapi():
    openapi_data = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_data, f, indent=2)
        f.write("\n")

def main():
    parser = argparse.ArgumentParser(description="AEP Example Server")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: serve
    parser_serve = subparsers.add_parser("serve", help="Start the server")

    # Subcommand: generate-openapi
    parser_generate = subparsers.add_parser("generate-openapi", help="Generate OpenAPI JSON")

    args = parser.parse_args()

    if args.command == "serve":
        run_server()
    elif args.command == "generate-openapi":
        generate_openapi()

if __name__ == "__main__":
    main()
