"""
AI Orchestrator - Multi-AI backend support
Supports OpenAI, Claude, and Ollama providers
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import json
import httpx
from config.settings import get_settings

settings = get_settings()

class AIProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"

class TaskType(Enum):
    TEXT_EXTRACTION = "text_extraction"
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    QUESTION_GENERATION = "question_generation"
    SUMMARIZATION = "summarization"
    FACE_ANALYSIS = "face_analysis"
    EVENT_EXTRACTION = "event_extraction"

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    async def process(self, task_type: TaskType, content: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process content with AI"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    def get_cost_per_token(self) -> float:
        """Get cost per token for this provider"""
        pass

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self):
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        except ImportError:
            self.client = None
    
    async def is_available(self) -> bool:
        return self.client is not None and settings.openai_api_key
    
    def get_cost_per_token(self) -> float:
        # Approximate costs per 1K tokens
        costs = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.001
        }
        return costs.get(self.model, 0.01)
    
    async def process(self, task_type: TaskType, content: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        if not await self.is_available():
            raise Exception("OpenAI not available")
        
        system_prompt = self._get_system_prompt(task_type, context)
        user_prompt = self._get_user_prompt(task_type, content, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return {
                "provider": AIProvider.OPENAI.value,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def _get_system_prompt(self, task_type: TaskType, context: Optional[Dict]) -> str:
        prompts = {
            TaskType.TEXT_EXTRACTION: "You are a genealogy data extraction expert. Extract genealogical information and return structured JSON.",
            TaskType.RELATIONSHIP_ANALYSIS: "You are a relationship analysis expert. Analyze family relationships and suggest connections.",
            TaskType.QUESTION_GENERATION: "You are a genealogy research assistant. Generate clarifying questions to fill information gaps.",
            TaskType.SUMMARIZATION: "You are a genealogy summarizer. Create concise summaries of family information.",
            TaskType.EVENT_EXTRACTION: "You are an event extraction expert. Identify and categorize life events from text."
        }
        return prompts.get(task_type, "You are a helpful genealogy assistant.")
    
    def _get_user_prompt(self, task_type: TaskType, content: str, context: Optional[Dict]) -> str:
        if task_type == TaskType.TEXT_EXTRACTION:
            return f"""Extract genealogical information from this text and return as JSON array:

{content}

Return entities with:
- entity_type: INDIVIDUAL, FAMILY, or EVENT
- data: extracted fields
- confidence: 0-1 score

Return only valid JSON."""
        
        elif task_type == TaskType.QUESTION_GENERATION:
            return f"""Based on this extracted genealogical data, generate clarifying questions:

{json.dumps(context, indent=2) if context else content}

Generate 3-5 specific questions to fill information gaps.
Return as JSON array of questions."""
        
        return content

class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self):
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=getattr(settings, 'claude_api_key', None))
            self.model = getattr(settings, 'claude_model', 'claude-3-sonnet-20240229')
        except ImportError:
            self.client = None
    
    async def is_available(self) -> bool:
        return self.client is not None and getattr(settings, 'claude_api_key', None)
    
    def get_cost_per_token(self) -> float:
        return 0.015  # Approximate Claude cost
    
    async def process(self, task_type: TaskType, content: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        if not await self.is_available():
            raise Exception("Claude not available")
        
        system_prompt = self._get_system_prompt(task_type, context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": content}
                ]
            )
            
            return {
                "provider": AIProvider.CLAUDE.value,
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
    
    def _get_system_prompt(self, task_type: TaskType, context: Optional[Dict]) -> str:
        prompts = {
            TaskType.TEXT_EXTRACTION: "Extract genealogical data as JSON. Return INDIVIDUAL, FAMILY, EVENT entities with confidence scores.",
            TaskType.RELATIONSHIP_ANALYSIS: "Analyze family relationships. Suggest parent-child, sibling, and spousal connections.",
            TaskType.QUESTION_GENERATION: "Generate specific questions to fill genealogical information gaps.",
            TaskType.SUMMARIZATION: "Summarize family history concisely.",
            TaskType.EVENT_EXTRACTION: "Extract life events with dates, locations, and participants."
        }
        return prompts.get(task_type, "You are a genealogy assistant.")

class OllamaProvider(BaseAIProvider):
    """Ollama local models provider"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ollama_url', 'http://localhost:11434')
        self.model = getattr(settings, 'ollama_model', 'llama2')
    
    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    def get_cost_per_token(self) -> float:
        return 0.0  # Local models are free
    
    async def process(self, task_type: TaskType, content: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        if not await self.is_available():
            raise Exception("Ollama not available")
        
        prompt = self._build_prompt(task_type, content, context)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama error: {response.text}")
                
                result = response.json()
                
                return {
                    "provider": AIProvider.OLLAMA.value,
                    "content": result.get("response", ""),
                    "usage": {
                        "total_tokens": len(prompt.split()) + len(result.get("response", "").split())
                    }
                }
        except Exception as e:
            raise Exception(f"Ollama processing error: {e}")
    
    def _build_prompt(self, task_type: TaskType, content: str, context: Optional[Dict]) -> str:
        base_prompt = f"You are a genealogy assistant. {content}"
        
        if task_type == TaskType.TEXT_EXTRACTION:
            return f"""{base_prompt}

Extract genealogical information and return as JSON:
- entity_type: INDIVIDUAL/FAMILY/EVENT  
- data: extracted fields
- confidence: 0-1

Text: {content}"""
        
        elif task_type == TaskType.QUESTION_GENERATION:
            return f"""{base_prompt}

Generate 3-5 clarifying questions based on:
{json.dumps(context, indent=2) if context else content}"""
        
        return base_prompt

class AIOrchestrator:
    """Main AI orchestrator that manages multiple providers"""
    
    def __init__(self):
        self.providers = {
            AIProvider.OPENAI: OpenAIProvider(),
            AIProvider.CLAUDE: ClaudeProvider(),
            AIProvider.OLLAMA: OllamaProvider()
        }
        
        # Provider preferences by task type
        self.task_preferences = {
            TaskType.TEXT_EXTRACTION: [AIProvider.OPENAI, AIProvider.CLAUDE, AIProvider.OLLAMA],
            TaskType.RELATIONSHIP_ANALYSIS: [AIProvider.CLAUDE, AIProvider.OPENAI, AIProvider.OLLAMA],
            TaskType.QUESTION_GENERATION: [AIProvider.CLAUDE, AIProvider.OPENAI, AIProvider.OLLAMA],
            TaskType.SUMMARIZATION: [AIProvider.OPENAI, AIProvider.CLAUDE, AIProvider.OLLAMA],
            TaskType.EVENT_EXTRACTION: [AIProvider.OPENAI, AIProvider.CLAUDE, AIProvider.OLLAMA],
            TaskType.FACE_ANALYSIS: [AIProvider.OPENAI, AIProvider.CLAUDE, AIProvider.OLLAMA]
        }
    
    async def process(self, task_type: TaskType, content: str, context: Optional[Dict] = None, 
                     preferred_provider: Optional[AIProvider] = None) -> Dict[str, Any]:
        """
        Process content with the best available AI provider
        """
        
        # Check availability of all providers
        available_providers = []
        provider_tasks = []
        
        for provider_enum, provider_instance in self.providers.items():
            task = asyncio.create_task(provider_instance.is_available())
            provider_tasks.append((provider_enum, task))
        
        for provider_enum, task in provider_tasks:
            try:
                if await task:
                    available_providers.append(provider_enum)
            except:
                continue
        
        if not available_providers:
            raise Exception("No AI providers available")
        
        # Select provider
        if preferred_provider and preferred_provider in available_providers:
            selected_provider = preferred_provider
        else:
            # Use task preferences or first available
            preferred_list = self.task_preferences.get(task_type, list(AIProvider))
            for provider in preferred_list:
                if provider in available_providers:
                    selected_provider = provider
                    break
            else:
                selected_provider = available_providers[0]
        
        # Process with selected provider
        provider_instance = self.providers[selected_provider]
        try:
            result = await provider_instance.process(task_type, content, context)
            result["selected_provider"] = selected_provider.value
            result["available_providers"] = [p.value for p in available_providers]
            return result
        except Exception as e:
            # Try fallback providers
            fallback_providers = [p for p in available_providers if p != selected_provider]
            
            for fallback_provider in fallback_providers:
                try:
                    fallback_instance = self.providers[fallback_provider]
                    result = await fallback_instance.process(task_type, content, context)
                    result["selected_provider"] = fallback_provider.value
                    result["fallback_from"] = selected_provider.value
                    result["available_providers"] = [p.value for p in available_providers]
                    return result
                except:
                    continue
            
            raise Exception(f"All providers failed. Last error: {e}")
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for provider_enum, provider_instance in self.providers.items():
            try:
                is_available = await provider_instance.is_available()
                status[provider_enum.value] = {
                    "available": is_available,
                    "cost_per_token": provider_instance.get_cost_per_token() if is_available else None
                }
            except Exception as e:
                status[provider_enum.value] = {
                    "available": False,
                    "error": str(e)
                }
        
        return status

# Global orchestrator instance
ai_orchestrator = AIOrchestrator()
