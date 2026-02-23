"""
Knowledge Base Service Implementation
Handles document processing, event extraction, and semantic search
"""
import os
import io
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import logging

# Document processing
import PyPDF2
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup

# Calendar processing
from icalendar import Calendar
import recurring_ical_events

# Text processing and NLP
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, and_, or_

from config.settings import get_settings
from src.database import KnowledgeDocument, ExtractedEvent, DocumentEmbedding
from src.models import (
    DocumentIngestionResponse, 
    EventExtractionResponse, 
    SearchResponse,
    CalendarEventResponse
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Spacy model not found. Some features may be limited.")
    nlp = None

class KnowledgeService:
    """Main knowledge base service"""
    
    def __init__(self):
        self.engine = create_async_engine(
            "postgresql+asyncpg://genealogy:genealogy@localhost:5432/genealogy_db",
            echo=settings.debug
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Initialize vectorizer for semantic search
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self._vectorizer_fitted = False
    
    async def ingest_document(
        self, 
        file, 
        title: str = None, 
        document_type: str = "auto",
        metadata: str = None
    ) -> DocumentIngestionResponse:
        """Ingest a document into the knowledge base"""
        
        try:
            # Read file content
            file_content = await file.read()
            filename = file.filename
            
            # Determine document type
            if document_type == "auto":
                document_type = self._detect_document_type(filename, file.content_type)
            
            # Extract text based on document type
            text_content = await self._extract_text(file_content, document_type)
            
            if not text_content or len(text_content.strip()) < 10:
                raise Exception("Could not extract meaningful text from document")
            
            # Parse metadata
            doc_metadata = {}
            if metadata:
                try:
                    doc_metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    logger.warning("Invalid metadata JSON provided")
            
            # Store document in database
            async with self.async_session() as session:
                document = KnowledgeDocument(
                    title=title or filename,
                    filename=filename,
                    document_type=document_type,
                    content=text_content,
                    metadata=json.dumps(doc_metadata),
                    file_size=len(file_content),
                    created_at=datetime.utcnow()
                )
                session.add(document)
                await session.commit()
                
                # Save file to disk
                await self._save_document_file(file_content, document.id, filename)
            
            # Extract events asynchronously
            extraction_task = asyncio.create_task(
                self.extract_events(str(document.id), text_content)
            )
            
            return DocumentIngestionResponse(
                document_id=str(document.id),
                title=document.title,
                document_type=document_type,
                status="ingested",
                events_extracted="pending",
                file_size=len(file_content)
            )
            
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            raise Exception(f"Document ingestion failed: {e}")
    
    async def extract_events(
        self, 
        document_id: str = None, 
        text: str = None,
        context: str = None
    ) -> EventExtractionResponse:
        """Extract genealogical events from document or text"""
        
        try:
            if document_id:
                # Get document from database
                async with self.async_session() as session:
                    result = await session.execute(
                        select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                    )
                    document = result.scalar_one_or_none()
                    
                    if not document:
                        raise Exception("Document not found")
                    
                    text = document.content
                    context = f"Document: {document.title}"
            elif not text:
                raise Exception("Either document_id or text must be provided")
            
            # Use AI to extract events
            from ..ingestion_service.src.ai_processor import extract_events_from_text
            
            events_data = await extract_events_from_text(text, {"context": context})
            
            extracted_events = []
            
            # Store events in database
            async with self.async_session() as session:
                for event_data in events_data:
                    event = ExtractedEvent(
                        document_id=document_id,
                        event_type=event_data.get("event_type", "UNKNOWN"),
                        event_date=self._parse_date(event_data.get("date")),
                        event_place=event_data.get("place"),
                        description=event_data.get("description"),
                        individuals_involved=json.dumps(event_data.get("individuals", [])),
                        confidence=event_data.get("confidence", 0.5),
                        source_data=json.dumps(event_data),
                        created_at=datetime.utcnow()
                    )
                    session.add(event)
                    extracted_events.append({
                        "event_id": str(event.id),
                        "event_type": event.event_type,
                        "event_date": event.event_date.isoformat() if event.event_date else None,
                        "event_place": event.event_place,
                        "description": event.description,
                        "confidence": event.confidence
                    })
                
                await session.commit()
            
            return EventExtractionResponse(
                document_id=document_id,
                events_extracted=len(extracted_events),
                events=extracted_events
            )
            
        except Exception as e:
            logger.error(f"Error extracting events: {e}")
            raise Exception(f"Event extraction failed: {e}")
    
    async def correlate_events(self, event_ids: List[str]) -> Dict[str, Any]:
        """Correlate and link related events"""
        
        try:
            async with self.async_session() as session:
                # Get events
                result = await session.execute(
                    select(ExtractedEvent).where(ExtractedEvent.id.in_(event_ids))
                )
                events = result.scalars().all()
                
                correlations = []
                
                # Simple correlation logic based on dates, locations, and people
                for i, event1 in enumerate(events):
                    for event2 in events[i+1:]:
                        correlation_score = self._calculate_event_correlation(event1, event2)
                        
                        if correlation_score > 0.5:  # Threshold for correlation
                            correlations.append({
                                "event1_id": str(event1.id),
                                "event2_id": str(event2.id),
                                "correlation_score": correlation_score,
                                "correlation_type": self._determine_correlation_type(event1, event2)
                            })
            
            return {
                "events_analyzed": len(events),
                "correlations_found": len(correlations),
                "correlations": correlations
            }
            
        except Exception as e:
            logger.error(f"Error correlating events: {e}")
            raise Exception(f"Event correlation failed: {e}")
    
    async def search(
        self, 
        query: str, 
        search_type: str = "semantic",
        limit: int = 20,
        filters: str = None
    ) -> SearchResponse:
        """Search the knowledge base"""
        
        try:
            # Parse filters
            search_filters = {}
            if filters:
                try:
                    search_filters = json.loads(filters)
                except json.JSONDecodeError:
                    logger.warning("Invalid filters JSON provided")
            
            results = []
            
            if search_type == "semantic":
                results = await self._semantic_search(query, limit, search_filters)
            elif search_type == "keyword":
                results = await self._keyword_search(query, limit, search_filters)
            elif search_type == "hybrid":
                # Combine both approaches
                semantic_results = await self._semantic_search(query, limit // 2, search_filters)
                keyword_results = await self._keyword_search(query, limit // 2, search_filters)
                
                # Merge and deduplicate
                seen_ids = set()
                for result in semantic_results + keyword_results:
                    if result["document_id"] not in seen_ids:
                        results.append(result)
                        seen_ids.add(result["document_id"])
            
            return SearchResponse(
                query=query,
                search_type=search_type,
                results=results[:limit],
                total_found=len(results)
            )
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            raise Exception(f"Search failed: {e}")
    
    async def ingest_calendar(
        self, 
        file, 
        calendar_type: str = "ics",
        date_range: str = None
    ) -> CalendarEventResponse:
        """Ingest calendar events"""
        
        try:
            file_content = await file.read()
            
            if calendar_type == "ics":
                events = await self._parse_ics_calendar(file_content, date_range)
            else:
                raise Exception(f"Unsupported calendar type: {calendar_type}")
            
            # Store calendar events as documents
            ingested_events = []
            
            async with self.async_session() as session:
                for event in events:
                    document = KnowledgeDocument(
                        title=event.get("summary", "Calendar Event"),
                        filename=file.filename,
                        document_type="calendar_event",
                        content=json.dumps(event),
                        metadata=json.dumps({
                            "calendar_type": calendar_type,
                            "event_start": event.get("dtstart"),
                            "event_end": event.get("dtend"),
                            "location": event.get("location")
                        }),
                        created_at=datetime.utcnow()
                    )
                    session.add(document)
                    ingested_events.append({
                        "event_id": str(document.id),
                        "summary": event.get("summary"),
                        "start": event.get("dtstart"),
                        "end": event.get("dtend"),
                        "location": event.get("location")
                    })
                
                await session.commit()
            
            return CalendarEventResponse(
                calendar_type=calendar_type,
                events_ingested=len(ingested_events),
                events=ingested_events
            )
            
        except Exception as e:
            logger.error(f"Error ingesting calendar: {e}")
            raise Exception(f"Calendar ingestion failed: {e}")
    
    async def get_documents(
        self, 
        limit: int = 50,
        document_type: str = None,
        date_range: str = None
    ) -> Dict[str, Any]:
        """Get list of ingested documents"""
        
        try:
            async with self.async_session() as session:
                query = select(KnowledgeDocument)
                
                if document_type:
                    query = query.where(KnowledgeDocument.document_type == document_type)
                
                if date_range:
                    try:
                        range_data = json.loads(date_range)
                        start_date = datetime.fromisoformat(range_data["start"])
                        end_date = datetime.fromisoformat(range_data["end"])
                        query = query.where(
                            and_(
                                KnowledgeDocument.created_at >= start_date,
                                KnowledgeDocument.created_at <= end_date
                            )
                        )
                    except (json.JSONDecodeError, KeyError):
                        logger.warning("Invalid date_range format")
                
                query = query.limit(limit)
                result = await session.execute(query)
                documents = result.scalars().all()
            
            doc_list = []
            for doc in documents:
                doc_list.append({
                    "document_id": str(doc.id),
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "file_size": doc.file_size,
                    "created_at": doc.created_at.isoformat()
                })
            
            return {
                "documents": doc_list,
                "total_count": len(doc_list)
            }
            
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            raise Exception(f"Failed to get documents: {e}")
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get document details and content"""
        
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                )
                document = result.scalar_one_or_none()
                
                if not document:
                    raise Exception("Document not found")
            
            return {
                "document_id": str(document.id),
                "title": document.title,
                "filename": document.filename,
                "document_type": document.document_type,
                "content": document.content,
                "metadata": json.loads(document.metadata) if document.metadata else {},
                "file_size": document.file_size,
                "created_at": document.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise Exception(f"Document not found: {e}")
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from knowledge base"""
        
        try:
            async with self.async_session() as session:
                # Delete document
                await session.execute(
                    delete(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
                )
                
                # Delete associated events
                await session.execute(
                    delete(ExtractedEvent).where(ExtractedEvent.document_id == document_id)
                )
                
                # Delete embeddings
                await session.execute(
                    delete(DocumentEmbedding).where(DocumentEmbedding.document_id == document_id)
                )
                
                await session.commit()
            
            # Delete file from disk
            await self._delete_document_file(document_id)
            
            return {"status": "deleted", "document_id": document_id}
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise Exception(f"Failed to delete document: {e}")
    
    async def get_events(
        self, 
        limit: int = 50,
        event_type: str = None,
        individual_id: str = None,
        date_range: str = None
    ) -> Dict[str, Any]:
        """Get extracted events"""
        
        try:
            async with self.async_session() as session:
                query = select(ExtractedEvent)
                
                if event_type:
                    query = query.where(ExtractedEvent.event_type == event_type)
                
                if individual_id:
                    query = query.where(
                        ExtractedEvent.individuals_involved.ilike(f"%{individual_id}%")
                    )
                
                if date_range:
                    try:
                        range_data = json.loads(date_range)
                        start_date = datetime.fromisoformat(range_data["start"])
                        end_date = datetime.fromisoformat(range_data["end"])
                        query = query.where(
                            and_(
                                ExtractedEvent.event_date >= start_date,
                                ExtractedEvent.event_date <= end_date
                            )
                        )
                    except (json.JSONDecodeError, KeyError):
                        logger.warning("Invalid date_range format")
                
                query = query.limit(limit)
                result = await session.execute(query)
                events = result.scalars().all()
            
            event_list = []
            for event in events:
                event_list.append({
                    "event_id": str(event.id),
                    "document_id": str(event.document_id),
                    "event_type": event.event_type,
                    "event_date": event.event_date.isoformat() if event.event_date else None,
                    "event_place": event.event_place,
                    "description": event.description,
                    "confidence": event.confidence,
                    "created_at": event.created_at.isoformat()
                })
            
            return {
                "events": event_list,
                "total_count": len(event_list)
            }
            
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            raise Exception(f"Failed to get events: {e}")
    
    async def generate_timeline(
        self, 
        individual_ids: List[str] = None,
        event_types: List[str] = None,
        date_range: str = None
    ) -> Dict[str, Any]:
        """Generate a timeline for individuals"""
        
        try:
            # Get events based on filters
            events_data = await self.get_events(
                limit=1000,  # Get more for timeline
                individual_id=individual_ids[0] if individual_ids else None,
                date_range=date_range
            )
            
            # Filter by event types if specified
            if event_types:
                events_data["events"] = [
                    event for event in events_data["events"]
                    if event["event_type"] in event_types
                ]
            
            # Sort events by date
            events_with_date = [
                event for event in events_data["events"]
                if event["event_date"]
            ]
            
            events_with_date.sort(key=lambda x: x["event_date"])
            
            # Group events by year/decade
            timeline = {}
            for event in events_with_date:
                year = datetime.fromisoformat(event["event_date"]).year
                if year not in timeline:
                    timeline[year] = []
                timeline[year].append(event)
            
            return {
                "timeline": timeline,
                "total_events": len(events_with_date),
                "date_range": {
                    "start": events_with_date[0]["event_date"] if events_with_date else None,
                    "end": events_with_date[-1]["event_date"] if events_with_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating timeline: {e}")
            raise Exception(f"Timeline generation failed: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        
        try:
            async with self.async_session() as session:
                # Document stats
                doc_result = await session.execute(select(KnowledgeDocument))
                total_documents = len(doc_result.scalars().all())
                
                # Event stats
                event_result = await session.execute(select(ExtractedEvent))
                total_events = len(event_result.scalars().all())
                
                # Document type breakdown
                type_query = select(
                    KnowledgeDocument.document_type,
                    func.count(KnowledgeDocument.id)
                ).group_by(KnowledgeDocument.document_type)
                type_result = await session.execute(type_query)
                doc_types = dict(type_result.all())
            
            return {
                "total_documents": total_documents,
                "total_events": total_events,
                "document_types": doc_types,
                "average_events_per_document": total_events / max(total_documents, 1),
                "search_index_size": "active" if self._vectorizer_fitted else "building"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise Exception(f"Failed to get stats: {e}")
    
    # Helper methods
    
    def _detect_document_type(self, filename: str, content_type: str) -> str:
        """Detect document type from filename and content type"""
        
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return 'pdf'
        elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            return 'image'
        elif filename_lower.endswith(('.txt', '.md')):
            return 'text'
        elif filename_lower.endswith(('.html', '.htm')):
            return 'html'
        elif filename_lower.endswith(('.doc', '.docx')):
            return 'document'
        elif filename_lower.endswith(('.ics', '.ical')):
            return 'calendar'
        else:
            return 'unknown'
    
    async def _extract_text(self, file_content: bytes, document_type: str) -> str:
        """Extract text from document based on type"""
        
        try:
            if document_type == 'pdf':
                return self._extract_pdf_text(file_content)
            elif document_type == 'image':
                return self._extract_image_text(file_content)
            elif document_type == 'text':
                return file_content.decode('utf-8')
            elif document_type == 'html':
                return self._extract_html_text(file_content)
            else:
                # Try to decode as text
                try:
                    return file_content.decode('utf-8')
                except UnicodeDecodeError:
                    return ""
                    
        except Exception as e:
            logger.error(f"Error extracting text from {document_type}: {e}")
            return ""
    
    def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting image text: {e}")
            return ""
    
    def _extract_html_text(self, file_content: bytes) -> str:
        """Extract text from HTML"""
        try:
            html_content = file_content.decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.error(f"Error extracting HTML text: {e}")
            return ""
    
    async def _save_document_file(self, file_content: bytes, document_id: str, filename: str):
        """Save document file to disk"""
        try:
            os.makedirs("documents", exist_ok=True)
            file_path = f"documents/{document_id}_{filename}"
            
            with open(file_path, "wb") as f:
                f.write(file_content)
                
        except Exception as e:
            logger.error(f"Error saving document file: {e}")
    
    async def _delete_document_file(self, document_id: str):
        """Delete document file from disk"""
        try:
            import glob
            files = glob.glob(f"documents/{document_id}_*")
            for file_path in files:
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting document file: {e}")
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object"""
        if not date_str:
            return None
        
        try:
            # Try various date formats
            formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%Y-%m-%d %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None
    
    def _calculate_event_correlation(self, event1, event2) -> float:
        """Calculate correlation score between two events"""
        score = 0.0
        
        # Date proximity (within 30 days)
        if event1.event_date and event2.event_date:
            days_diff = abs((event1.event_date - event2.event_date).days)
            if days_diff <= 30:
                score += 0.3
            elif days_diff <= 365:
                score += 0.1
        
        # Location similarity
        if event1.event_place and event2.event_place:
            if event1.event_place.lower() == event2.event_place.lower():
                score += 0.4
            elif any(word in event1.event_place.lower() for word in event2.event_place.lower().split()):
                score += 0.2
        
        # Event type relationship
        type_relationships = {
            ("BIRTH", "DEATH"): 0.2,
            ("BIRTH", "MARRIAGE"): 0.3,
            ("MARRIAGE", "DEATH"): 0.2,
            ("BIRTH", "BIRTH"): 0.1,  # Siblings
            ("MARRIAGE", "MARRIAGE"): 0.1  # Family events
        }
        
        event_pair = (event1.event_type, event2.event_type)
        if event_pair in type_relationships:
            score += type_relationships[event_pair]
        elif (event_pair[1], event_pair[0]) in type_relationships:
            score += type_relationships[(event_pair[1], event_pair[0])]
        
        return min(score, 1.0)
    
    def _determine_correlation_type(self, event1, event2) -> str:
        """Determine type of correlation between events"""
        
        if event1.event_type == event2.event_type:
            return "same_type"
        elif event1.event_place and event2.event_place:
            if event1.event_place.lower() == event2.event_place.lower():
                return "same_location"
        elif event1.event_date and event2.event_date:
            days_diff = abs((event1.event_date - event2.event_date).days)
            if days_diff <= 7:
                return "same_time"
        
        return "related"
    
    async def _semantic_search(self, query: str, limit: int, filters: Dict) -> List[Dict]:
        """Perform semantic search using TF-IDF"""
        
        try:
            async with self.async_session() as session:
                # Get all documents
                result = await session.execute(select(KnowledgeDocument))
                documents = result.scalars().all()
            
            if not documents:
                return []
            
            # Prepare documents and query
            doc_texts = [doc.content for doc in documents]
            
            # Fit vectorizer if not already fitted
            if not self._vectorizer_fitted:
                self.vectorizer.fit(doc_texts)
                self._vectorizer_fitted = True
            
            # Transform query and documents
            try:
                query_vec = self.vectorizer.transform([query])
                doc_vecs = self.vectorizer.transform(doc_texts)
                
                # Calculate similarities
                similarities = cosine_similarity(query_vec, doc_vecs)[0]
                
                # Get top results
                top_indices = similarities.argsort()[-limit:][::-1]
                
                results = []
                for idx in top_indices:
                    if similarities[idx] > 0.1:  # Minimum similarity threshold
                        doc = documents[idx]
                        results.append({
                            "document_id": str(doc.id),
                            "title": doc.title,
                            "document_type": doc.document_type,
                            "similarity": float(similarities[idx]),
                            "snippet": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                        })
                
                return results
                
            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return []
    
    async def _keyword_search(self, query: str, limit: int, filters: Dict) -> List[Dict]:
        """Perform keyword search"""
        
        try:
            async with self.async_session() as session:
                # Build search query
                search_query = select(KnowledgeDocument).where(
                    or_(
                        KnowledgeDocument.title.ilike(f"%{query}%"),
                        KnowledgeDocument.content.ilike(f"%{query}%")
                    )
                )
                
                # Apply filters
                if "document_type" in filters:
                    search_query = search_query.where(
                        KnowledgeDocument.document_type == filters["document_type"]
                    )
                
                search_query = search_query.limit(limit)
                result = await session.execute(search_query)
                documents = result.scalars().all()
            
            results = []
            for doc in documents:
                results.append({
                    "document_id": str(doc.id),
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "similarity": 1.0,  # Perfect match for keyword search
                    "snippet": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing keyword search: {e}")
            return []
    
    async def _parse_ics_calendar(self, file_content: bytes, date_range: str = None) -> List[Dict]:
        """Parse ICS calendar file"""
        
        try:
            calendar_text = file_content.decode('utf-8')
            cal = Calendar.from_ical(calendar_text)
            
            events = []
            
            # Parse date range if provided
            start_date = None
            end_date = None
            if date_range:
                try:
                    range_data = json.loads(date_range)
                    start_date = datetime.fromisoformat(range_data["start"])
                    end_date = datetime.fromisoformat(range_data["end"])
                except (json.JSONDecodeError, KeyError):
                    logger.warning("Invalid date_range format for calendar")
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event_data = {
                        "summary": str(component.get("summary", "")),
                        "description": str(component.get("description", "")),
                        "location": str(component.get("location", "")),
                        "dtstart": component.get("dtstart").dt,
                        "dtend": component.get("dtend").dt
                    }
                    
                    # Filter by date range if specified
                    if start_date and end_date:
                        event_start = event_data["dtstart"]
                        if isinstance(event_start, datetime):
                            if event_start < start_date or event_start > end_date:
                                continue
                    
                    events.append(event_data)
            
            return events
            
        except Exception as e:
            logger.error(f"Error parsing ICS calendar: {e}")
            return []
