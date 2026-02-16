import openai
from typing import Dict, Any, List
from config.settings import get_settings
import json

settings = get_settings()
openai.api_key = settings.openai_api_key

async def extract_genealogical_data(text: str) -> List[Dict[str, Any]]:
    """
    Use OpenAI to extract genealogical entities from text.
    Returns a list of extracted entities (individuals, families, events)
    """
    
    prompt = """You are a genealogy data extraction expert. Extract genealogical information from the following text and return it as JSON.

Extract the following entity types when present:
1. INDIVIDUAL - a person with name, birth date, birth place, death date, death place, sex
2. FAMILY - marriage/partnership with spouses and children
3. EVENT - births, deaths, marriages, censuses, etc.

For the text below, extract all genealogical entities and return as a JSON array with objects containing:
- entity_type: string (INDIVIDUAL, FAMILY, EVENT)
- data: object with extracted fields
- confidence: float (0-1) representing confidence in extraction

Text to extract from:
{text}

Return only valid JSON, no additional text.""".format(text=text)
    
    try:
        response = await openai.ChatCompletion.acreate(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a genealogy data extraction expert. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content
        
        # Parse JSON response
        entities = json.loads(response_text)
        if not isinstance(entities, list):
            entities = [entities]
        
        return entities
    
    except json.JSONDecodeError as e:
        print(f"Error parsing OpenAI response: {e}")
        return []
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []

async def generate_summary(text: str) -> str:
    """Generate a summary of the text"""
    
    try:
        response = await openai.ChatCompletion.acreate(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes genealogical information."},
                {"role": "user", "content": f"Summarize this genealogical information:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return ""
