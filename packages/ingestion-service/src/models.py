from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ContentType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    PDF = "pdf"
    CARDDAV = "carddav"

class SourceType(str, Enum):
    TELEGRAM = "telegram"
    CARDDAV = "carddav"
    FILE = "file"
    MANUAL = "manual"

class IngestRequest(BaseModel):
    content: str
    content_type: ContentType
    source_type: SourceType
    source_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ExtractedEntity(BaseModel):
    entity_type: str  # INDIVIDUAL, FAMILY, EVENT, etc.
    data: Dict[str, Any]
    confidence: float = Field(ge=0, le=1)

class IngestResponse(BaseModel):
    ingestion_id: str
    status: str  # PENDING, PROCESSING, SUCCESS, ERROR
    extracted_entities: List[ExtractedEntity] = []
    error_message: Optional[str] = None
    raw_response: Optional[str] = None

class VoiceTranscriptionRequest(BaseModel):
    file_path: str
    language: str = "en"

class DocumentExtractionRequest(BaseModel):
    file_path: str
    document_type: str = "auto"

class CardDAVContactRequest(BaseModel):
    vcf_content: str

class CardDAVContactResponse(BaseModel):
    name: str
    given_names: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    note: Optional[str] = None
