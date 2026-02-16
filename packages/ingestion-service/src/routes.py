from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
import uuid
import os
from src.models import IngestRequest, IngestResponse, ExtractedEntity, CardDAVContactRequest
from src.ai_processor import extract_genealogical_data, generate_summary
from src.carddav_parser import parse_vcf, parse_vcf_file
from src.document_processor import (
    transcribe_voice, extract_text_from_image, extract_text_from_pdf,
    is_supported_audio, is_supported_image, is_supported_pdf
)
from config.settings import get_settings

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])
settings = get_settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

@router.post("/text", response_model=IngestResponse)
async def ingest_text(request: IngestRequest):
    """Ingest and process text data for genealogical information"""
    
    ingestion_id = str(uuid.uuid4())
    
    try:
        # Extract entities using AI
        extracted_data = await extract_genealogical_data(request.content)
        
        # Convert to our entities format
        entities = []
        for item in extracted_data:
            entity = ExtractedEntity(
                entity_type=item.get('entity_type', 'UNKNOWN'),
                data=item.get('data', {}),
                confidence=item.get('confidence', 0.5)
            )
            entities.append(entity)
        
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="success",
            extracted_entities=entities,
            raw_response=request.content
        )
    
    except Exception as e:
        print(f"Error processing text ingestion: {e}")
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="error",
            error_message=str(e)
        )

@router.post("/voice", response_model=IngestResponse)
async def ingest_voice(file: UploadFile = File(...)):
    """Ingest and process voice messages"""
    
    ingestion_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = os.path.join(settings.upload_dir, f"{ingestion_id}_{file.filename}")
        
        with open(file_path, 'wb') as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Check if supported audio format
        if not is_supported_audio(file_path):
            return IngestResponse(
                ingestion_id=ingestion_id,
                status="error",
                error_message="Unsupported audio format. Supported: MP3, WAV, M4A, OGG, FLAC"
            )
        
        # Transcribe audio
        transcript = await transcribe_voice(file_path)
        
        # Extract genealogical data from transcript
        extracted_data = await extract_genealogical_data(transcript)
        
        entities = []
        for item in extracted_data:
            entity = ExtractedEntity(
                entity_type=item.get('entity_type', 'UNKNOWN'),
                data=item.get('data', {}),
                confidence=item.get('confidence', 0.5)
            )
            entities.append(entity)
        
        # Cleanup
        os.remove(file_path)
        
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="success",
            extracted_entities=entities,
            raw_response=transcript
        )
    
    except Exception as e:
        print(f"Error processing voice ingestion: {e}")
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="error",
            error_message=str(e)
        )

@router.post("/image", response_model=IngestResponse)
async def ingest_image(file: UploadFile = File(...)):
    """Ingest and process images for OCR"""
    
    ingestion_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = os.path.join(settings.upload_dir, f"{ingestion_id}_{file.filename}")
        
        with open(file_path, 'wb') as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Check if supported image format
        if not is_supported_image(file_path):
            return IngestResponse(
                ingestion_id=ingestion_id,
                status="error",
                error_message="Unsupported image format. Supported: JPG, PNG, BMP, GIF, TIFF"
            )
        
        # Extract text from image
        text = await extract_text_from_image(file_path)
        
        # Extract genealogical data
        extracted_data = await extract_genealogical_data(text)
        
        entities = []
        for item in extracted_data:
            entity = ExtractedEntity(
                entity_type=item.get('entity_type', 'UNKNOWN'),
                data=item.get('data', {}),
                confidence=item.get('confidence', 0.5)
            )
            entities.append(entity)
        
        # Cleanup
        os.remove(file_path)
        
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="success",
            extracted_entities=entities,
            raw_response=text
        )
    
    except Exception as e:
        print(f"Error processing image ingestion: {e}")
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="error",
            error_message=str(e)
        )

@router.post("/pdf", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """Ingest and process PDF documents"""
    
    ingestion_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = os.path.join(settings.upload_dir, f"{ingestion_id}_{file.filename}")
        
        with open(file_path, 'wb') as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Check if PDF
        if not is_supported_pdf(file_path):
            return IngestResponse(
                ingestion_id=ingestion_id,
                status="error",
                error_message="File is not a PDF"
            )
        
        # Extract text from PDF
        text = await extract_text_from_pdf(file_path)
        
        # Extract genealogical data
        extracted_data = await extract_genealogical_data(text)
        
        entities = []
        for item in extracted_data:
            entity = ExtractedEntity(
                entity_type=item.get('entity_type', 'UNKNOWN'),
                data=item.get('data', {}),
                confidence=item.get('confidence', 0.5)
            )
            entities.append(entity)
        
        # Cleanup
        os.remove(file_path)
        
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="success",
            extracted_entities=entities,
            raw_response=text
        )
    
    except Exception as e:
        print(f"Error processing PDF ingestion: {e}")
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="error",
            error_message=str(e)
        )

@router.post("/carddav", response_model=IngestResponse)
async def ingest_carddav(request: CardDAVContactRequest):
    """Ingest vCard/CardDAV contacts"""
    
    ingestion_id = str(uuid.uuid4())
    
    try:
        contacts = [parse_vcf(request.vcf_content)]
        
        # Convert to genealogical entities
        entities = []
        for contact in contacts:
            entity = ExtractedEntity(
                entity_type="INDIVIDUAL",
                data={
                    "given_names": contact.given_names,
                    "surname": contact.surname,
                    "birth_date": contact.birth_date,
                    "email": contact.email,
                    "phone": contact.phone,
                    "note": contact.note
                },
                confidence=0.9
            )
            entities.append(entity)
        
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="success",
            extracted_entities=entities
        )
    
    except Exception as e:
        print(f"Error processing CardDAV ingestion: {e}")
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="error",
            error_message=str(e)
        )

@router.post("/carddav-file", response_model=IngestResponse)
async def ingest_carddav_file(file: UploadFile = File(...)):
    """Ingest vCard/CardDAV file with multiple contacts"""
    
    ingestion_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = os.path.join(settings.upload_dir, f"{ingestion_id}_{file.filename}")
        
        with open(file_path, 'wb') as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Parse vCard file
        contacts = parse_vcf_file(file_path)
        
        # Convert to genealogical entities
        entities = []
        for contact in contacts:
            entity = ExtractedEntity(
                entity_type="INDIVIDUAL",
                data={
                    "given_names": contact.given_names,
                    "surname": contact.surname,
                    "birth_date": contact.birth_date,
                    "email": contact.email,
                    "phone": contact.phone,
                    "note": contact.note
                },
                confidence=0.9
            )
            entities.append(entity)
        
        # Cleanup
        os.remove(file_path)
        
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="success",
            extracted_entities=entities
        )
    
    except Exception as e:
        print(f"Error processing CardDAV file ingestion: {e}")
        return IngestResponse(
            ingestion_id=ingestion_id,
            status="error",
            error_message=str(e)
        )
