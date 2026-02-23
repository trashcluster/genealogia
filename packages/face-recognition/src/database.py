"""
Database models for Face Recognition Service
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class FaceEmbedding(Base):
    """Store face embeddings for recognition"""
    __tablename__ = "face_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    individual_id = Column(String(255), nullable=True, index=True)  # Link to individuals table
    person_name = Column(String(255), nullable=True, index=True)
    embedding = Column(Text, nullable=False)  # JSON array of face embedding
    model_version = Column(String(50), default="facenet")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = relationship("FaceImage", back_populates="face_embedding")

class FaceImage(Base):
    """Store metadata about face images"""
    __tablename__ = "face_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    face_embedding_id = Column(UUID(as_uuid=True), ForeignKey("face_embeddings.id"), nullable=False)
    individual_id = Column(String(255), nullable=True, index=True)
    person_name = Column(String(255), nullable=True)
    image_path = Column(String(500), nullable=False)
    image_width = Column(Integer)
    image_height = Column(Integer)
    face_metadata = Column(Text)  # JSON with bounding box, landmarks, etc.
    quality_score = Column(Float)  # Image quality assessment
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    face_embedding = relationship("FaceEmbedding", back_populates="images")

class FaceCluster(Base):
    """Store face clustering results"""
    __tablename__ = "face_clusters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(Integer, nullable=False, index=True)
    face_embedding_id = Column(UUID(as_uuid=True), ForeignKey("face_embeddings.id"), nullable=False)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    face_embedding = relationship("FaceEmbedding")

class FaceProcessingLog(Base):
    """Log face processing operations"""
    __tablename__ = "face_processing_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_type = Column(String(50), nullable=False)  # DETECT, MATCH, REGISTER, etc.
    image_path = Column(String(500))
    faces_detected = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    success = Column(String(10), default="true")  # true/false
    error_message = Column(Text)
    metadata = Column(Text)  # JSON with additional details
    created_at = Column(DateTime, default=datetime.utcnow)
