"""
Knowledge Base Service
Handles document ingestion, event extraction, and semantic search for genealogy
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from src.knowledge_service import KnowledgeService
from src.models import (
    DocumentIngestionResponse, 
    EventExtractionResponse, 
    SearchResponse,
    CalendarEventResponse
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
knowledge_service = KnowledgeService()

app = FastAPI(
    title="Genealogy Knowledge Base Service",
    version="0.1.0",
    description="Document ingestion and knowledge management for family history"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest-document", response_model=DocumentIngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),
    title: str = None,
    document_type: str = "auto",  # auto, pdf, image, text, calendar
    metadata: str = None  # JSON string with additional metadata
):
    """Ingest a document into the knowledge base"""
    try:
        result = await knowledge_service.ingest_document(
            file, title, document_type, metadata
        )
        return result
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(500, f"Document ingestion failed: {e}")

@app.post("/extract-events", response_model=EventExtractionResponse)
async def extract_events(
    document_id: str = None,
    text: str = None,
    context: str = None
):
    """Extract genealogical events from document or text"""
    try:
        result = await knowledge_service.extract_events(document_id, text, context)
        return result
    except Exception as e:
        logger.error(f"Error extracting events: {e}")
        raise HTTPException(500, f"Event extraction failed: {e}")

@app.post("/correlate-events")
async def correlate_events(event_ids: list[str]):
    """Correlate and link related events"""
    try:
        result = await knowledge_service.correlate_events(event_ids)
        return result
    except Exception as e:
        logger.error(f"Error correlating events: {e}")
        raise HTTPException(500, f"Event correlation failed: {e}")

@app.get("/search", response_model=SearchResponse)
async def search_knowledge(
    query: str,
    search_type: str = "semantic",  # semantic, keyword, hybrid
    limit: int = 20,
    filters: str = None  # JSON string with search filters
):
    """Search the knowledge base"""
    try:
        result = await knowledge_service.search(query, search_type, limit, filters)
        return result
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(500, f"Search failed: {e}")

@app.post("/ingest-calendar", response_model=CalendarEventResponse)
async def ingest_calendar(
    file: UploadFile = File(...),
    calendar_type: str = "ics",  # ics, google, outlook
    date_range: str = None  # JSON with start/end dates
):
    """Ingest calendar events"""
    try:
        result = await knowledge_service.ingest_calendar(file, calendar_type, date_range)
        return result
    except Exception as e:
        logger.error(f"Error ingesting calendar: {e}")
        raise HTTPException(500, f"Calendar ingestion failed: {e}")

@app.get("/documents")
async def get_documents(
    limit: int = 50,
    document_type: str = None,
    date_range: str = None
):
    """Get list of ingested documents"""
    try:
        result = await knowledge_service.get_documents(limit, document_type, date_range)
        return result
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(500, f"Failed to get documents: {e}")

@app.get("/document/{document_id}")
async def get_document(document_id: str):
    """Get document details and content"""
    try:
        result = await knowledge_service.get_document(document_id)
        return result
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(404, f"Document not found: {e}")

@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from knowledge base"""
    try:
        result = await knowledge_service.delete_document(document_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(500, f"Failed to delete document: {e}")

@app.get("/events")
async def get_events(
    limit: int = 50,
    event_type: str = None,
    individual_id: str = None,
    date_range: str = None
):
    """Get extracted events"""
    try:
        result = await knowledge_service.get_events(limit, event_type, individual_id, date_range)
        return result
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(500, f"Failed to get events: {e}")

@app.post("/generate-timeline")
async def generate_timeline(
    individual_ids: list[str] = None,
    event_types: list[str] = None,
    date_range: str = None
):
    """Generate a timeline for individuals"""
    try:
        result = await knowledge_service.generate_timeline(individual_ids, event_types, date_range)
        return result
    except Exception as e:
        logger.error(f"Error generating timeline: {e}")
        raise HTTPException(500, f"Timeline generation failed: {e}")

@app.get("/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        result = await knowledge_service.get_stats()
        return result
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(500, f"Failed to get stats: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "document_ingestion": "active",
            "event_extraction": "active",
            "semantic_search": "active"
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Genealogy Knowledge Base Service",
        "version": "0.1.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=settings.debug
    )
