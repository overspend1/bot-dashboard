"""Main FastAPI application."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

from app.config import settings
from app.database import init_db, SessionLocal
from app.services.bot_manager import bot_manager
from app.routers import bots, auth, stats, websocket
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Bot Management Dashboard...")

    # Ensure required directories exist
    os.makedirs(settings.BOTS_DIR, exist_ok=True)
    os.makedirs(settings.LOGS_DIR, exist_ok=True)
    os.makedirs(settings.CONFIGS_DIR, exist_ok=True)
    os.makedirs("./data", exist_ok=True)

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Start bot manager monitoring
    logger.info("Starting bot manager...")
    bot_manager.start_monitoring()

    # Load existing bots from database
    db = SessionLocal()
    try:
        bot_manager.load_bots_from_db(db)
    finally:
        db.close()

    logger.info("Bot Management Dashboard started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down Bot Management Dashboard...")

    # Stop all bots
    db = SessionLocal()
    try:
        bot_manager.stop_all_bots(db)
    finally:
        db.close()

    # Stop monitoring
    bot_manager.stop_monitoring()

    logger.info("Bot Management Dashboard shut down successfully!")


# Create FastAPI application
app = FastAPI(
    title="Bot Management Dashboard API",
    description="API for managing Telegram and Discord bots",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing."""
    request_id = f"{int(time.time() * 1000)}"
    start_time = time.time()

    logger.info(f"[{request_id}] {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- Error: {str(e)} - Duration: {duration:.3f}s"
        )
        raise


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    logger.warning(f"Validation error for {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, "body") else None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error for {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.LOG_LEVEL == "DEBUG" else "An error occurred",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns:
        Status of the API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "production" if settings.SECRET_KEY != "dev-secret-key-change-in-production" else "development",
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with API information.

    Returns:
        API welcome message
    """
    return {
        "message": "Bot Management Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(auth.router)
app.include_router(bots.router)
app.include_router(stats.router)
app.include_router(websocket.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
