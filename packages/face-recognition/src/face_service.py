"""
Face Recognition Service Implementation
Handles face detection, embedding generation, and database operations
"""
import os
import io
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import face_recognition
import cv2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
import json
import logging
from datetime import datetime

from config.settings import get_settings
from src.database import FaceEmbedding, FaceImage
from src.models import FaceDetectionResponse, FaceMatchResponse, PersonFaceResponse

logger = logging.getLogger(__name__)
settings = get_settings()

class FaceRecognitionService:
    """Main face recognition service"""
    
    def __init__(self):
        self.engine = create_async_engine(
            "postgresql+asyncpg://genealogy:genealogy@localhost:5432/genealogy_db",
            echo=settings.debug
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.similarity_threshold = settings.face_similarity_threshold
        
    async def detect_faces(self, image_file) -> FaceDetectionResponse:
        """Detect faces in an image and return bounding boxes"""
        
        try:
            # Read image
            image_data = await image_file.read()
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            
            # Detect face locations
            face_locations = face_recognition.face_locations(image, model="hog")
            
            # Detect face landmarks for better alignment
            face_landmarks_list = face_recognition.face_landmarks(image)
            
            faces = []
            for i, (top, right, bottom, left) in enumerate(face_locations):
                face_data = {
                    "id": f"face_{i}",
                    "bounding_box": {
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "left": left
                    },
                    "confidence": 0.95,  # face_recognition doesn't provide confidence
                    "landmarks": face_landmarks_list[i] if i < len(face_landmarks_list) else None
                }
                faces.append(face_data)
            
            return FaceDetectionResponse(
                faces_detected=len(face_locations),
                faces=faces,
                image_width=image.shape[1],
                image_height=image.shape[0]
            )
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            raise Exception(f"Face detection failed: {e}")
    
    async def match_faces(self, image_file) -> FaceMatchResponse:
        """Detect faces and find matches in database"""
        
        try:
            # Detect faces
            detection_result = await self.detect_faces(image_file)
            
            if detection_result.faces_detected == 0:
                return FaceMatchResponse(
                    faces_detected=0,
                    matches=[],
                    unmatched_faces=[]
                )
            
            # Read image for embedding generation
            image_data = await image_file.read()
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            
            # Generate face encodings
            face_encodings = face_recognition.face_encodings(
                image, 
                known_face_locations=[(f["bounding_box"]["top"], f["bounding_box"]["right"], 
                                      f["bounding_box"]["bottom"], f["bounding_box"]["left"]) 
                                     for f in detection_result.faces]
            )
            
            # Get all stored face embeddings from database
            async with self.async_session() as session:
                result = await session.execute(select(FaceEmbedding))
                stored_faces = result.scalars().all()
            
            matches = []
            unmatched_faces = []
            
            for i, face_encoding in enumerate(face_encodings):
                face_data = detection_result.faces[i]
                
                # Compare with stored faces
                best_match = None
                best_similarity = 0
                
                for stored_face in stored_faces:
                    stored_embedding = np.array(json.loads(stored_face.embedding))
                    
                    # Calculate face distance (lower is more similar)
                    distance = face_recognition.face_distance([stored_embedding], face_encoding)[0]
                    similarity = 1 - distance  # Convert to similarity score
                    
                    if similarity > best_similarity and similarity >= self.similarity_threshold:
                        best_similarity = similarity
                        best_match = stored_face
                
                if best_match:
                    match_data = {
                        "face_id": face_data["id"],
                        "individual_id": best_match.individual_id,
                        "person_name": best_match.person_name,
                        "similarity": best_similarity,
                        "confidence": min(0.95, best_similarity),
                        "bounding_box": face_data["bounding_box"]
                    }
                    matches.append(match_data)
                else:
                    unmatched_faces.append({
                        "face_id": face_data["id"],
                        "bounding_box": face_data["bounding_box"],
                        "suggested_action": "register_new_person"
                    })
            
            return FaceMatchResponse(
                faces_detected=detection_result.faces_detected,
                matches=matches,
                unmatched_faces=unmatched_faces
            )
            
        except Exception as e:
            logger.error(f"Error matching faces: {e}")
            raise Exception(f"Face matching failed: {e}")
    
    async def register_face(self, image_file, individual_id: str = None, person_name: str = None):
        """Register a new face for an individual"""
        
        try:
            # Detect faces first
            detection_result = await self.detect_faces(image_file)
            
            if detection_result.faces_detected == 0:
                raise Exception("No faces detected in image")
            elif detection_result.faces_detected > 1:
                raise Exception("Multiple faces detected. Please provide an image with a single face.")
            
            # Read image for embedding generation
            image_data = await image_file.read()
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            
            # Generate face encoding
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                raise Exception("Could not generate face encoding")
            
            face_encoding = face_encodings[0]
            
            # Store in database
            async with self.async_session() as session:
                # Store face embedding
                face_embedding = FaceEmbedding(
                    individual_id=individual_id,
                    person_name=person_name,
                    embedding=json.dumps(face_encoding.tolist()),
                    created_at=datetime.utcnow()
                )
                session.add(face_embedding)
                
                # Store face image metadata
                face_image = FaceImage(
                    individual_id=individual_id,
                    person_name=person_name,
                    image_path=f"faces/{face_embedding.id}.jpg",
                    face_metadata=json.dumps(detection_result.faces[0]),
                    created_at=datetime.utcnow()
                )
                session.add(face_image)
                
                await session.commit()
                
                # Save image file
                await self._save_face_image(image_data, face_embedding.id)
            
            return {
                "face_id": str(face_embedding.id),
                "individual_id": individual_id,
                "person_name": person_name,
                "status": "registered"
            }
            
        except Exception as e:
            logger.error(f"Error registering face: {e}")
            raise Exception(f"Face registration failed: {e}")
    
    async def get_person_faces(self, individual_id: str) -> PersonFaceResponse:
        """Get all registered faces for an individual"""
        
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(FaceEmbedding).where(FaceEmbedding.individual_id == individual_id)
                )
                faces = result.scalars().all()
            
            face_list = []
            for face in faces:
                face_data = {
                    "face_id": str(face.id),
                    "person_name": face.person_name,
                    "created_at": face.created_at.isoformat(),
                    "image_count": 1  # Simplified for now
                }
                face_list.append(face_data)
            
            return PersonFaceResponse(
                individual_id=individual_id,
                face_count=len(face_list),
                faces=face_list
            )
            
        except Exception as e:
            logger.error(f"Error getting person faces: {e}")
            raise Exception(f"Failed to get person faces: {e}")
    
    async def delete_face(self, face_id: str):
        """Delete a face registration"""
        
        try:
            async with self.async_session() as session:
                # Delete face embedding
                await session.execute(
                    delete(FaceEmbedding).where(FaceEmbedding.id == face_id)
                )
                
                # Delete face image
                await session.execute(
                    delete(FaceImage).where(FaceImage.individual_id == face_id)
                )
                
                await session.commit()
                
                # Delete image file
                await self._delete_face_image(face_id)
            
            return {"status": "deleted", "face_id": face_id}
            
        except Exception as e:
            logger.error(f"Error deleting face: {e}")
            raise Exception(f"Failed to delete face: {e}")
    
    async def search_faces(self, query: str = None, individual_id: str = None, limit: int = 20):
        """Search for faces by name or individual"""
        
        try:
            async with self.async_session() as session:
                stmt = select(FaceEmbedding).limit(limit)
                
                if individual_id:
                    stmt = stmt.where(FaceEmbedding.individual_id == individual_id)
                elif query:
                    stmt = stmt.where(FaceEmbedding.person_name.ilike(f"%{query}%"))
                
                result = await session.execute(stmt)
                faces = result.scalars().all()
            
            search_results = []
            for face in faces:
                face_data = {
                    "face_id": str(face.id),
                    "individual_id": face.individual_id,
                    "person_name": face.person_name,
                    "created_at": face.created_at.isoformat()
                }
                search_results.append(face_data)
            
            return {
                "query": query,
                "individual_id": individual_id,
                "results": search_results,
                "total_count": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error searching faces: {e}")
            raise Exception(f"Face search failed: {e}")
    
    async def cluster_faces(self, image_ids: List[str] = None):
        """Cluster similar faces to identify potential duplicates"""
        
        try:
            async with self.async_session() as session:
                stmt = select(FaceEmbedding)
                if image_ids:
                    stmt = stmt.where(FaceEmbedding.id.in_(image_ids))
                
                result = await session.execute(stmt)
                faces = result.scalars().all()
            
            if len(faces) < 2:
                return {"clusters": [], "message": "Need at least 2 faces for clustering"}
            
            # Extract embeddings
            embeddings = []
            face_data = []
            
            for face in faces:
                embedding = np.array(json.loads(face.embedding))
                embeddings.append(embedding)
                face_data.append({
                    "face_id": str(face.id),
                    "person_name": face.person_name,
                    "individual_id": face.individual_id
                })
            
            embeddings = np.array(embeddings)
            
            # Simple clustering based on similarity threshold
            clusters = []
            used_indices = set()
            
            for i in range(len(embeddings)):
                if i in used_indices:
                    continue
                
                cluster = [face_data[i]]
                used_indices.add(i)
                
                for j in range(i + 1, len(embeddings)):
                    if j in used_indices:
                        continue
                    
                    distance = face_recognition.face_distance([embeddings[i]], embeddings[j])[0]
                    similarity = 1 - distance
                    
                    if similarity >= self.similarity_threshold:
                        cluster.append(face_data[j])
                        used_indices.add(j)
                
                if len(cluster) > 1:
                    clusters.append({
                        "cluster_id": len(clusters) + 1,
                        "faces": cluster,
                        "similarity_threshold": self.similarity_threshold
                    })
            
            return {
                "clusters": clusters,
                "total_faces": len(faces),
                "clusters_found": len(clusters)
            }
            
        except Exception as e:
            logger.error(f"Error clustering faces: {e}")
            raise Exception(f"Face clustering failed: {e}")
    
    async def get_stats(self):
        """Get face recognition statistics"""
        
        try:
            async with self.async_session() as session:
                # Total faces
                total_faces_result = await session.execute(select(FaceEmbedding))
                total_faces = len(total_faces_result.scalars().all())
                
                # Unique individuals
                unique_individuals_result = await session.execute(
                    select(FaceEmbedding.individual_id).distinct()
                )
                unique_individuals = len(unique_individuals_result.scalars().all())
            
            return {
                "total_faces_registered": total_faces,
                "unique_individuals": unique_individuals,
                "average_faces_per_person": total_faces / max(unique_individuals, 1),
                "similarity_threshold": self.similarity_threshold,
                "service_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise Exception(f"Failed to get stats: {e}")
    
    async def _save_face_image(self, image_data: bytes, face_id: str):
        """Save face image to disk"""
        try:
            os.makedirs("faces", exist_ok=True)
            image_path = f"faces/{face_id}.jpg"
            
            with open(image_path, "wb") as f:
                f.write(image_data)
                
        except Exception as e:
            logger.error(f"Error saving face image: {e}")
    
    async def _delete_face_image(self, face_id: str):
        """Delete face image from disk"""
        try:
            image_path = f"faces/{face_id}.jpg"
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            logger.error(f"Error deleting face image: {e}")
