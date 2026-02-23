"""
Enhanced AI processor with multi-provider support
"""
from typing import Dict, Any, List
from .ai_orchestrator import ai_orchestrator, TaskType, AIProvider
import json
import logging

logger = logging.getLogger(__name__)

async def extract_genealogical_data(text: str, preferred_provider: AIProvider = None) -> List[Dict[str, Any]]:
    """
    Use AI to extract genealogical entities from text.
    Returns a list of extracted entities (individuals, families, events)
    """
    
    try:
        result = await ai_orchestrator.process(
            TaskType.TEXT_EXTRACTION, 
            text, 
            preferred_provider=preferred_provider
        )
        
        logger.info(f"Used provider: {result.get('selected_provider')}")
        
        # Parse JSON response
        try:
            entities = json.loads(result["content"])
            if not isinstance(entities, list):
                entities = [entities]
            
            # Add provider metadata
            for entity in entities:
                entity["extracted_by"] = result.get("selected_provider")
                entity["confidence_adjusted"] = adjust_confidence(
                    entity.get("confidence", 0.5), 
                    result.get("selected_provider")
                )
            
            return entities
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            # Fallback: try to extract basic info manually
            return extract_basic_fallback(text)
    
    except Exception as e:
        logger.error(f"Error calling AI API: {e}")
        return []

async def analyze_relationships(individuals: List[Dict], families: List[Dict]) -> List[Dict[str, Any]]:
    """Analyze and suggest relationships between individuals"""
    
    context = {
        "individuals": individuals,
        "families": families
    }
    
    try:
        result = await ai_orchestrator.process(
            TaskType.RELATIONSHIP_ANALYSIS,
            json.dumps(context, indent=2),
            context=context
        )
        
        suggestions = json.loads(result["content"])
        return suggestions if isinstance(suggestions, list) else [suggestions]
    
    except Exception as e:
        logger.error(f"Error analyzing relationships: {e}")
        return []

async def generate_clarifying_questions(extracted_data: Dict[str, Any], information_gaps: List[str]) -> List[str]:
    """Generate questions to fill information gaps"""
    
    context = {
        "extracted_data": extracted_data,
        "information_gaps": information_gaps
    }
    
    try:
        result = await ai_orchestrator.process(
            TaskType.QUESTION_GENERATION,
            json.dumps(context, indent=2),
            context=context
        )
        
        questions = json.loads(result["content"])
        return questions if isinstance(questions, list) else [questions]
    
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return []

async def extract_events_from_text(text: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Extract life events from text"""
    
    try:
        result = await ai_orchestrator.process(
            TaskType.EVENT_EXTRACTION,
            text,
            context=context
        )
        
        events = json.loads(result["content"])
        return events if isinstance(events, list) else [events]
    
    except Exception as e:
        logger.error(f"Error extracting events: {e}")
        return []

async def generate_summary(text: str) -> str:
    """Generate a summary of the text"""
    
    try:
        result = await ai_orchestrator.process(
            TaskType.SUMMARIZATION,
            text
        )
        
        return result["content"]
    
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return ""

async def get_ai_provider_status() -> Dict[str, Any]:
    """Get status of all AI providers"""
    return await ai_orchestrator.get_provider_status()

def adjust_confidence(base_confidence: float, provider: str) -> float:
    """Adjust confidence based on provider reliability"""
    
    provider_reliability = {
        "openai": 1.0,
        "claude": 0.95,
        "ollama": 0.85
    }
    
    return min(1.0, base_confidence * provider_reliability.get(provider, 0.8))

def extract_basic_fallback(text: str) -> List[Dict[str, Any]]:
    """Basic fallback extraction when AI fails"""
    
    entities = []
    
    # Very basic pattern matching
    import re
    
    # Extract names (basic pattern)
    name_patterns = [
        r'([A-Z][a-z]+ [A-Z][a-z]+) was born',
        r'([A-Z][a-z]+ [A-Z][a-z]+) married',
        r'My ([a-z]+) ([A-Z][a-z]+)'
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                name = " ".join(match)
            else:
                name = match
            
            entities.append({
                "entity_type": "INDIVIDUAL",
                "data": {
                    "name": name,
                    "confidence": 0.3
                },
                "confidence": 0.3,
                "extracted_by": "fallback"
            })
    
    return entities
