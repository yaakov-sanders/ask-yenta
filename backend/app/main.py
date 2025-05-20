import logging
import traceback
from collections.abc import Callable
from contextlib import asynccontextmanager
from http.client import HTTPException

import pydevd_pycharm
import sentry_sdk
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.config import settings
from app.features.core.api_main import api_router
from app.features.core.models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.info("Starting application with logging enabled")


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:

            logger.error(
                f"Unhandled exception: {type(e).__name__}: {str(e)}\n"
                f"Path: {request.url.path}\n"
                f"Method: {request.method}\n"
                f"Traceback: {traceback.format_exc()}"
            )

            # Return a 500 response
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    detail="Internal server error",
                    error_code="server_error"
                ).model_dump(),
            )


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    try:
        pydevd_pycharm.settrace('host.docker.internal', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
    except Exception:
        pass
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

# Add exception handling middleware
app.add_middleware(ExceptionMiddleware)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
