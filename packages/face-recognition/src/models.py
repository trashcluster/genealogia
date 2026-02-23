"""
Pydantic models for Face Recognition Service
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class BoundingBox(BaseModel):
    top: int
    right: int
    bottom: int
    left: int

class FaceData(BaseModel):
    id: str
    bounding_box: BoundingBox
    confidence: float
    landmarks: Optional[Dict[str, Any]] = None

class FaceDetectionResponse(BaseModel):
    faces_detected: int
    faces: List[FaceData]
    image_width: int
    image_height: int

class FaceMatch(BaseModel):
    face_id: str
    individual_id: Optional[str]
    person_name: Optional[str]
    similarity: float
    confidence: float
    bounding_box: BoundingBox

class UnmatchedFace(BaseModel):
    face_id: str
    bounding_box: BoundingBox
    suggested_action: str

class FaceMatchResponse(BaseModel):
    faces_detected: int
    matches: List[FaceMatch]
    unmatched_faces: List[UnmatchedFace]

class PersonFace(BaseModel):
    face_id: str
    person_name: Optional[str]
    created_at: str
    image_count: int

class PersonFaceResponse(BaseModel):
    individual_id: str
    face_count: int
    faces: List[PersonFace]

class FaceRegistration(BaseModel):
    face_id: str
    individual_id: Optional[str]
    person_name: Optional[str]
    status: str

class SearchResult(BaseModel):
    face_id: str
    individual_id: Optional[str]
    person_name: Optional[str]
    created_at: str

class FaceSearchResponse(BaseModel):
    query: Optional[str]
    individual_id: Optional[str]
    results: List[SearchResult]
    total_count: int

class ClusterFace(BaseModel):
    face_id: str
    person_name: Optional[str]
    individual_id: Optional[str]

class FaceCluster(BaseModel):
    cluster_id: int
    faces: List[ClusterFace]
    similarity_threshold: float

class FaceClusterResponse(BaseModel):
    clusters: List[FaceCluster]
    total_faces: int
    clusters_found: int

class FaceStats(BaseModel):
    total_faces_registered: int
    unique_individuals: int
    average_faces_per_person: float
    similarity_threshold: float
    service_status: str
