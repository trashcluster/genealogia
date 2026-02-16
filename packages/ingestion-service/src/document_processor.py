from pydub import AudioSegment
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import os
from typing import Optional

async def transcribe_voice(file_path: str, language: str = "en") -> str:
    """
    Transcribe voice message using OpenAI Whisper API.
    In production, consider using a proper async implementation.
    """
    
    import openai
    from config.settings import get_settings
    
    settings = get_settings()
    
    try:
        with open(file_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        
        return transcript.get('text', '')
    
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

async def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from image using OCR (Tesseract).
    Useful for processing family photos with text or document images.
    """
    
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

async def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using OCR.
    Useful for processing scanned documents.
    """
    
    try:
        images = convert_from_path(file_path)
        full_text = ""
        
        for image in images:
            text = pytesseract.image_to_string(image)
            full_text += text + "\n"
        
        return full_text
    
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def get_file_extension(file_path: str) -> str:
    """Get file extension"""
    return os.path.splitext(file_path)[1].lower()

def is_supported_audio(file_path: str) -> bool:
    """Check if file is supported audio format"""
    supported = ['.mp3', '.wav', '.m4a', '.ogg', '.flac']
    return get_file_extension(file_path) in supported

def is_supported_image(file_path: str) -> bool:
    """Check if file is supported image format"""
    supported = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    return get_file_extension(file_path) in supported

def is_supported_pdf(file_path: str) -> bool:
    """Check if file is PDF"""
    return get_file_extension(file_path) == '.pdf'
