import logging
import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.core.database import Base, engine
from app.models.expense_model import Expense
from app.routers import expense_router


app = FastAPI(title="Expense Service")
logger = logging.getLogger("uvicorn.error")

default_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://localhost:5500",
    "https://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
]

raw_origins = os.getenv("BACKEND_CORS_ORIGINS")
if raw_origins:
    extra_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    allowed_origins = list(dict.fromkeys(default_origins + extra_origins))
else:
    allowed_origins = default_origins
logger.info("Configured CORS origins: %s", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS origin regex: %s", r"https?://(localhost|127\.0\.0\.1)(:\d+)?$")


@app.on_event("startup")
def create_tables():
    retries = 5
    while retries:
        try:
            Base.metadata.create_all(bind=engine, tables=[Expense.__table__])
            break
        except OperationalError:
            retries -= 1
            time.sleep(2)
    else:
        raise RuntimeError("Database unavailable, could not create expenses tables.")


app.include_router(expense_router.router)


@app.get("/")
def root():
    return {"message": "Expense Service is running"}
