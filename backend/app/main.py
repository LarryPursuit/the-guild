"""The Guild API: app setup, CORS, error handlers and routers.

Run locally with:  uvicorn app.main:app --reload
Interactive docs:  http://localhost:8000/docs
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .config import CORS_ORIGINS
from .database import Base, engine
from .routers import auth, guilds, quests, users

logger = logging.getLogger("the_guild")

# Creates any missing tables on startup. (For a bigger project, use Alembic migrations.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="The Guild API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Turn Pydantic's validation details into one readable message for the frontend."""
    messages = []
    for err in exc.errors():
        field = err["loc"][-1] if err.get("loc") else "input"
        msg = err.get("msg", "is invalid").removeprefix("Value error, ")
        messages.append(f"{str(field).replace('_', ' ').capitalize()}: {msg}")
    return JSONResponse(status_code=422, content={"detail": "; ".join(messages) or "Invalid input."})


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error")
    return JSONResponse(status_code=500, content={"detail": "A database error occurred. Please try again."})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error")
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on our end."})


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(guilds.router)
app.include_router(quests.router)
