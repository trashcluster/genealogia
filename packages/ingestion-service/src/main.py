from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from src.routes import router as ingest_router

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-powered genealogical data ingestion service"
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
app.include_router(ingest_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.api_version
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Genealogy Ingestion Service",
        "version": settings.api_version,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )
