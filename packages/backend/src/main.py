from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from src.routes_auth import router as auth_router
from src.routes_individuals import router as individuals_router
from src.models import HealthResponse

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Genealogy data API with AI ingestion"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(individuals_router)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Genealogy API",
        "version": settings.api_version,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
