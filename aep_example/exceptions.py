from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .models import ProblemDetails

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    problem = ProblemDetails(
        type="aep.example.com/http-error",
        title=exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
        status=exc.status_code,
        detail=str(exc.detail) if not isinstance(exc.detail, str) else None,
        instance=str(request.url)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json"
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    problem = ProblemDetails(
        type="aep.example.com/validation-error",
        title="Validation Error",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
        instance=str(request.url)
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json"
    )
