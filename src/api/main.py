import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    companies,
    documents,
    health,
    peers,
    portfolio,
    screener,
    sectors,
    valuation,
)

DB_PATH = "nifty100.db"
START_TIME = time.time()

app = FastAPI(
    title="N100 Financial Intelligence API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging
@app.middleware("http")
async def request_logging(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    elapsed = time.time() - start

    print(f"{request.method} " f"{request.url.path} " f"{elapsed:.4f}s")

    return response


# API routers
API_PREFIX = "/api/v1"

app.include_router(
    companies.router,
    prefix=API_PREFIX + "/companies",
    tags=["Companies"],
)

app.include_router(
    screener.router,
    prefix=API_PREFIX + "/screener",
    tags=["Screener"],
)

app.include_router(
    sectors.router,
    prefix=API_PREFIX + "/sectors",
    tags=["Sectors"],
)

app.include_router(
    peers.router,
    prefix=API_PREFIX + "/peers",
    tags=["Peers"],
)

app.include_router(
    valuation.router,
    prefix=API_PREFIX,
    tags=["Valuation"],
)

app.include_router(
    portfolio.router,
    prefix=API_PREFIX + "/portfolio",
    tags=["Portfolio"],
)

app.include_router(
    documents.router,
    prefix=API_PREFIX,
    tags=["Documents"],
)

app.include_router(
    health.router,
    prefix=API_PREFIX,
    tags=["Health"],
)


@app.get("/")
def root():
    return {
        "message": "N100 Financial Intelligence API",
        "docs": "/docs",
    }
