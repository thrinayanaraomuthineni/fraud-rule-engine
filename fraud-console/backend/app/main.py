from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .database import Base, engine
from .routes import dashboard, reviews, transactions


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Fraud Rule Engine", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(transactions.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)


@app.exception_handler(SQLAlchemyError)
async def db_error(_: Request, exc: SQLAlchemyError):
    return JSONResponse({"detail": "Database error. Please retry."}, status_code=500)
