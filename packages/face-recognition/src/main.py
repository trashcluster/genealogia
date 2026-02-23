"""
Face Recognition Service
Handles face detection, embedding generation, and matching for genealogy photos
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from src.face_service import FaceRecognitionService
from src.models import FaceDetectionResponse, FaceMatchResponse, PersonFaceResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
face_service = FaceRecognitionService()

app = FastAPI(
    title="Genealogy Face Recognition Service",
    version="0.1.0",
    description="Face detection and matching for family photos"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/detect-faces", response_model=FaceDetectionResponse)
async def detect_faces(image: UploadFile = File(...)):
    """Detect faces in an uploaded image"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        result = await face_service.detect_faces(image)
        return result
    except Exception as e:
        logger.error(f"Error detecting faces: {e}")
        raise HTTPException(500, f"Face detection failed: {e}")

@app.post("/match-faces", response_model=FaceMatchResponse)
async def match_faces(image: UploadFile = File(...)):
    """Detect faces and find matches in database"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        result = await face_service.match_faces(image)
        return result
    except Exception as e:
        logger.error(f"Error matching faces: {e}")
        raise HTTPException(500, f"Face matching failed: {e}")

@app.post("/register-face")
async def register_face(
    image: UploadFile = File(...),
    individual_id: str = None,
    person_name: str = None
):
    """Register a face for an individual"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        if not individual_id and not person_name:
            raise HTTPException(400, "Either individual_id or person_name required")
        
        result = await face_service.register_face(image, individual_id, person_name)
        return result
    except Exception as e:
        logger.error(f"Error registering face: {e}")
        raise HTTPException(500, f"Face registration failed: {e}")

@app.get("/person-faces/{individual_id}", response_model=PersonFaceResponse)
async def get_person_faces(individual_id: str):
    """Get all registered faces for an individual"""
    try:
        result = await face_service.get_person_faces(individual_id)
        return result
    except Exception as e:
        logger.error(f"Error getting person faces: {e}")
        raise HTTPException(500, f"Failed to get person faces: {e}")

@app.delete("/face/{face_id}")
async def delete_face(face_id: str):
    """Delete a face registration"""
    try:
        result = await face_service.delete_face(face_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting face: {e}")
        raise HTTPException(500, f"Failed to delete face: {e}")

@app.get("/search-faces")
async def search_faces(
    query: str = None,
    individual_id: str = None,
    limit: int = 20
):
    """Search for faces by name or individual"""
    try:
        result = await face_service.search_faces(query, individual_id, limit)
        return result
    except Exception as e:
        logger.error(f"Error searching faces: {e}")
        raise HTTPException(500, f"Face search failed: {e}")

@app.post("/cluster-faces")
async def cluster_faces(image_ids: list[str] = None):
    """Cluster similar faces to identify potential duplicates"""
    try:
        result = await face_service.cluster_faces(image_ids)
        return result
    except Exception as e:
        logger.error(f"Error clustering faces: {e}")
        raise HTTPException(500, f"Face clustering failed: {e}")

@app.get("/stats")
async def get_face_stats():
    """Get face recognition statistics"""
    try:
        result = await face_service.get_stats()
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
        "face_recognition_enabled": settings.face_recognition_enabled
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Genealogy Face Recognition Service",
        "version": "0.1.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=settings.debug
    )
