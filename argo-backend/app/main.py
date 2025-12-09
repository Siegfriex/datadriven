from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.middleware import ErrorHandlingMiddleware
from app.routers import (
    artists, institutions, exhibitions, transactions, 
    clusters, analysis, anomalies, search, galaxy
)

settings = get_settings()

app = FastAPI(
    title="ARGO Backend API",
    description="Backend API for Art-world Real-time Galaxy Observatory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(artists.router)
app.include_router(institutions.router)
app.include_router(exhibitions.router)
app.include_router(transactions.router)
app.include_router(clusters.router)
app.include_router(analysis.router)
app.include_router(anomalies.router)
app.include_router(search.router)
app.include_router(galaxy.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
