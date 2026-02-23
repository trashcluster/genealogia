"""
Conversation Engine for Telegram Bot
Handles interactive questioning and context-aware dialogue
"""
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    QUESTIONING = "questioning"
    CLARIFYING = "clarifying"
    CONFIRMING = "confirming"

@dataclass
class ConversationContext:
    user_id: str
    chat_id: str
    state: ConversationState
    current_data: Dict[str, Any]
    pending_questions: List[str]
    answered_questions: Dict[str, str]
    session_start: datetime
    last_activity: datetime

class ConversationEngine:
    """Interactive conversation engine for genealogy data collection"""
    
    def __init__(self, ingestion_service_url: str, backend_service_url: str):
        self.ingestion_service_url = ingestion_service_url
        self.backend_service_url = backend_service_url
        self.active_conversations: Dict[str, ConversationContext] = {}
        
        # Question templates for different scenarios
        self.question_templates = {
            "missing_birth_date": [
                "When was {name} born?",
                "Do you know {name}'s birth date?",
                "What year was {name} born in?"
            ],
            "missing_birth_place": [
                "Where was {name} born?",
                "Do you know {name}'s birthplace?",
                "In which city/country was {name} born?"
            ],
            "missing_death_date": [
                "When did {name} pass away?",
                "Do you know {name}'s date of death?",
                "What year did {name} die?"
            ],
            "missing_death_place": [
                "Where did {name} pass away?",
                "Do you know {name}'s place of death?",
                "In which location did {name} die?"
            ],
            "missing_parents": [
                "Who were {name}'s parents?",
                "Do you know the names of {name}'s mother and father?",
                "Can you tell me about {name}'s parents?"
            ],
            "missing_spouse": [
                "Was {name} married? If so, what was their spouse's name?",
                "Do you know who {name} married?",
                "Tell me about {name}'s marriage"
            ],
            "missing_children": [
                "Did {name} have any children?",
                "Can you tell me about {name}'s children?",
                "What were the names of {name}'s children?"
            ],
            "relationship_clarification": [
                "How is {person1} related to {person2}?",
                "Can you clarify the relationship between {person1} and {person2}?",
                "Are {person1} and {person2} related? If so, how?"
            ],
            "event_details": [
                "Can you tell me more about this {event_type}?",
                "Do you have any additional details about the {event_type}?",
                "What else can you tell me about this {event_type}?"
            ]
        }
    
    async def start_conversation(self, user_id: str, chat_id: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation session"""
        
        try:
            # Create conversation context
            context = ConversationContext(
                user_id=user_id,
                chat_id=chat_id,
                state=ConversationState.PROCESSING,
                current_data=initial_data,
                pending_questions=[],
                answered_questions={},
                session_start=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            # Store context
            conversation_key = f"{user_id}_{chat_id}"
            self.active_conversations[conversation_key] = context
            
            # Analyze initial data and identify gaps
            gaps = await self._identify_information_gaps(initial_data)
            
            if gaps:
                # Generate questions
                questions = await self._generate_clarifying_questions(gaps, initial_data)
                context.pending_questions = questions
                context.state = ConversationState.QUESTIONING
                
                return {
                    "status": "questions_needed",
                    "message": "I've extracted some information, but I have a few questions to help me build a more complete family tree.",
                    "questions": questions[:3],  # Start with first 3 questions
                    "total_questions": len(questions)
                }
            else:
                # No gaps found, proceed with data storage
                result = await self._finalize_conversation(context)
                return result
                
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return {
                "status": "error",
                "message": "I had trouble processing that information. Could you try rephrasing?"
            }
    
    async def process_response(self, user_id: str, chat_id: str, response: str) -> Dict[str, Any]:
        """Process user response in conversation"""
        
        try:
            conversation_key = f"{user_id}_{chat_id}"
            context = self.active_conversations.get(conversation_key)
            
            if not context:
                # Start new conversation with this response
                return await self.start_conversation(user_id, chat_id, {"text": response})
            
            context.last_activity = datetime.utcnow()
            
            # Process based on current state
            if context.state == ConversationState.QUESTIONING:
                return await self._handle_question_response(context, response)
            elif context.state == ConversationState.CLARIFYING:
                return await self._handle_clarification_response(context, response)
            elif context.state == ConversationState.CONFIRMING:
                return await self._handle_confirmation_response(context, response)
            else:
                # Treat as new information
                return await self._process_new_information(context, response)
                
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            return {
                "status": "error",
                "message": "I didn't understand that. Could you try again?"
            }
    
    async def _identify_information_gaps(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify missing information in extracted data"""
        
        gaps = []
        
        # Check for individuals with missing information
        individuals = data.get("individuals", [])
        for individual in individuals:
            person_data = individual.get("data", {})
            name = person_data.get("given_names", "") + " " + person_data.get("surname", "")
            name = name.strip()
            
            if not name:
                continue
            
            # Check for missing basic information
            if not person_data.get("birth_date"):
                gaps.append({
                    "type": "missing_birth_date",
                    "person": name,
                    "individual_id": individual.get("id"),
                    "priority": "high"
                })
            
            if not person_data.get("birth_place"):
                gaps.append({
                    "type": "missing_birth_place",
                    "person": name,
                    "individual_id": individual.get("id"),
                    "priority": "medium"
                })
            
            # Check for death information (if person might be deceased)
            if self._might_be_deceased(person_data):
                if not person_data.get("death_date"):
                    gaps.append({
                        "type": "missing_death_date",
                        "person": name,
                        "individual_id": individual.get("id"),
                        "priority": "medium"
                    })
            
            # Check for relationships
            if not person_data.get("family_relationships"):
                gaps.append({
                    "type": "missing_parents",
                    "person": name,
                    "individual_id": individual.get("id"),
                    "priority": "high"
                })
        
        # Check for relationship clarity
        families = data.get("families", [])
        for family in families:
            family_data = family.get("data", {})
            if not family_data.get("spouses") or len(family_data.get("spouses", [])) < 2:
                gaps.append({
                    "type": "missing_spouse",
                    "family_id": family.get("id"),
                    "priority": "medium"
                })
        
        # Sort by priority
        gaps.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}[x.get("priority", "low")], reverse=True)
        
        return gaps[:10]  # Limit to 10 most important gaps
    
    async def _generate_clarifying_questions(self, gaps: List[Dict], data: Dict) -> List[str]:
        """Generate clarifying questions based on information gaps"""
        
        questions = []
        
        for gap in gaps:
            gap_type = gap.get("type")
            templates = self.question_templates.get(gap_type, [])
            
            if templates:
                # Select a template and format it
                template = templates[0]  # Use first template for now
                
                if "person" in gap:
                    question = template.format(name=gap["person"])
                elif "person1" in gap and "person2" in gap:
                    question = template.format(person1=gap["person1"], person2=gap["person2"])
                elif "event_type" in gap:
                    question = template.format(event_type=gap["event_type"])
                else:
                    question = template
                
                questions.append(question)
        
        return questions
    
    async def _handle_question_response(self, context: ConversationContext, response: str) -> Dict[str, Any]:
        """Handle response to a clarification question"""
        
        try:
            # Store the answer
            if context.pending_questions:
                current_question = context.pending_questions[0]
                context.answered_questions[current_question] = response
                context.pending_questions.pop(0)
            
            # Try to extract information from the response
            extracted_info = await self._extract_information_from_response(response)
            
            if extracted_info:
                # Merge with current data
                context.current_data = self._merge_data(context.current_data, extracted_info)
            
            # Check if there are more questions
            if context.pending_questions:
                return {
                    "status": "continue_questions",
                    "message": "Thanks! I have a few more questions:",
                    "questions": context.pending_questions[:3],
                    "remaining_questions": len(context.pending_questions)
                }
            else:
                # No more questions, move to confirmation
                context.state = ConversationState.CONFIRMING
                summary = await self._generate_summary(context.current_data)
                
                return {
                    "status": "confirmation_needed",
                    "message": "Thank you! Based on what you've told me, here's what I've understood:",
                    "summary": summary,
                    "actions": ["confirm", "edit", "add_more"]
                }
                
        except Exception as e:
            logger.error(f"Error handling question response: {e}")
            return {
                "status": "error",
                "message": "I had trouble understanding that. Could you try again?"
            }
    
    async def _handle_clarification_response(self, context: ConversationContext, response: str) -> Dict[str, Any]:
        """Handle response to clarification request"""
        
        # Similar to question response but for clarification
        return await self._handle_question_response(context, response)
    
    async def _handle_confirmation_response(self, context: ConversationContext, response: str) -> Dict[str, Any]:
        """Handle confirmation response"""
        
        response_lower = response.lower()
        
        if "confirm" in response_lower or "yes" in response_lower or "correct" in response_lower:
            # User confirmed, finalize the conversation
            result = await self._finalize_conversation(context)
            return result
        elif "edit" in response_lower or "change" in response_lower or "wrong" in response_lower:
            # User wants to edit
            context.state = ConversationState.CLARIFYING
            return {
                "status": "edit_mode",
                "message": "What would you like to change? Please tell me what information is incorrect.",
                "current_data": context.current_data
            }
        elif "add" in response_lower or "more" in response_lower:
            # User wants to add more information
            context.state = ConversationState.QUESTIONING
            return {
                "status": "add_more",
                "message": "Great! What additional information would you like to share?",
                "suggestions": [
                    "Tell me about more family members",
                    "Add important life events",
                    "Share family photos or documents",
                    "Describe family relationships"
                ]
            }
        else:
            # Unclear response
            return {
                "status": "unclear",
                "message": "I'm not sure what you mean. Would you like to confirm this information, make changes, or add more details?"
            }
    
    async def _process_new_information(self, context: ConversationContext, response: str) -> Dict[str, Any]:
        """Process new information outside of Q&A flow"""
        
        try:
            # Extract information from the response
            extracted_info = await self._extract_information_from_response(response)
            
            if extracted_info:
                # Merge with current data
                context.current_data = self._merge_data(context.current_data, extracted_info)
                
                # Check if we need more questions
                gaps = await self._identify_information_gaps(context.current_data)
                
                if gaps:
                    questions = await self._generate_clarifying_questions(gaps, context.current_data)
                    context.pending_questions = questions
                    context.state = ConversationState.QUESTIONING
                    
                    return {
                        "status": "new_questions",
                        "message": "Thanks for that information! I have a few questions to help me complete the picture:",
                        "questions": questions[:3],
                        "total_questions": len(questions)
                    }
                else:
                    # Move to confirmation
                    context.state = ConversationState.CONFIRMING
                    summary = await self._generate_summary(context.current_data)
                    
                    return {
                        "status": "confirmation_needed",
                        "message": "Great! Here's what I've understood from everything you've shared:",
                        "summary": summary,
                        "actions": ["confirm", "edit", "add_more"]
                    }
            else:
                return {
                    "status": "no_info_extracted",
                    "message": "I didn't find any genealogical information in that. Could you tell me about family members, important dates, or relationships?"
                }
                
        except Exception as e:
            logger.error(f"Error processing new information: {e}")
            return {
                "status": "error",
                "message": "I had trouble processing that. Could you try rephrasing?"
            }
    
    async def _extract_information_from_response(self, response: str) -> Dict[str, Any]:
        """Extract genealogical information from user response"""
        
        try:
            # Use AI service to extract information
            import httpx
            
            async with httpx.AsyncClient() as client:
                result = await client.post(
                    f"{self.ingestion_service_url}/api/ingest/text",
                    json={
                        "content": response,
                        "content_type": "text",
                        "source_type": "telegram_response"
                    }
                )
                
                if result.status_code == 200:
                    return result.json()
                else:
                    logger.error(f"AI service error: {result.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error extracting information from response: {e}")
            return {}
    
    async def _finalize_conversation(self, context: ConversationContext) -> Dict[str, Any]:
        """Finalize conversation and store data"""
        
        try:
            # Send data to backend service
            import httpx
            
            async with httpx.AsyncClient() as client:
                result = await client.post(
                    f"{self.backend_service_url}/api/ingest/batch",
                    json=context.current_data,
                    headers={"Authorization": f"Bearer {context.current_data.get('api_key')}"}
                )
                
                if result.status_code == 200:
                    # Clean up conversation
                    conversation_key = f"{context.user_id}_{context.chat_id}"
                    if conversation_key in self.active_conversations:
                        del self.active_conversations[conversation_key]
                    
                    return {
                        "status": "completed",
                        "message": "Perfect! I've added all this information to your family tree. Is there anything else you'd like to share?",
                        "stored_data": result.json()
                    }
                else:
                    logger.error(f"Backend service error: {result.status_code}")
                    return {
                        "status": "error",
                        "message": "I had trouble saving this information. Please try again later."
                    }
                    
        except Exception as e:
            logger.error(f"Error finalizing conversation: {e}")
            return {
                "status": "error",
                "message": "Something went wrong while saving your information."
            }
    
    async def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the collected data"""
        
        try:
            individuals = data.get("individuals", [])
            families = data.get("families", [])
            events = data.get("events", [])
            
            summary_parts = []
            
            if individuals:
                if len(individuals) == 1:
                    summary_parts.append(f"I found information about 1 person")
                else:
                    summary_parts.append(f"I found information about {len(individuals)} people")
                
                # List names
                names = []
                for individual in individuals[:5]:  # Limit to first 5
                    person_data = individual.get("data", {})
                    name = f"{person_data.get('given_names', '')} {person_data.get('surname', '')}".strip()
                    if name:
                        names.append(name)
                
                if names:
                    summary_parts.append(f"Names: {', '.join(names)}")
            
            if families:
                summary_parts.append(f"I identified {len(families)} family relationships")
            
            if events:
                summary_parts.append(f"I found {len(events)} important events")
            
            return " | ".join(summary_parts) if summary_parts else "I've collected some family information"
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "I've collected some family information"
    
    def _merge_data(self, current_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new data with current data"""
        
        merged = current_data.copy()
        
        # Merge individuals
        current_individuals = merged.get("individuals", [])
        new_individuals = new_data.get("individuals", [])
        
        for new_individual in new_individuals:
            # Check if this person already exists (by name similarity)
            person_data = new_individual.get("data", {})
            new_name = f"{person_data.get('given_names', '')} {person_data.get('surname', '')}".strip()
            
            existing_person = None
            for existing in current_individuals:
                existing_data = existing.get("data", {})
                existing_name = f"{existing_data.get('given_names', '')} {existing_data.get('surname', '')}".strip()
                
                if new_name.lower() == existing_name.lower():
                    existing_person = existing
                    break
            
            if existing_person:
                # Merge with existing person
                existing_data = existing_person.get("data", {})
                for key, value in person_data.items():
                    if value and not existing_data.get(key):
                        existing_data[key] = value
            else:
                # Add new person
                current_individuals.append(new_individual)
        
        merged["individuals"] = current_individuals
        
        # Merge other data types
        for data_type in ["families", "events", "sources"]:
            current_items = merged.get(data_type, [])
            new_items = new_data.get(data_type, [])
            current_items.extend(new_items)
            merged[data_type] = current_items
        
        return merged
    
    def _might_be_deceased(self, person_data: Dict[str, Any]) -> bool:
        """Simple heuristic to determine if a person might be deceased"""
        
        # If birth date is more than 100 years ago, likely deceased
        birth_date = person_data.get("birth_date")
        if birth_date:
            try:
                birth_year = int(birth_date.split("-")[0])
                if datetime.utcnow().year - birth_year > 100:
                    return True
            except:
                pass
        
        return False
    
    async def get_conversation_status(self, user_id: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get current conversation status"""
        
        conversation_key = f"{user_id}_{chat_id}"
        context = self.active_conversations.get(conversation_key)
        
        if not context:
            return None
        
        return {
            "state": context.state.value,
            "session_duration": (datetime.utcnow() - context.session_start).total_seconds(),
            "questions_remaining": len(context.pending_questions),
            "data_collected": len(context.current_data.get("individuals", []))
        }
    
    async def end_conversation(self, user_id: str, chat_id: str) -> bool:
        """End active conversation"""
        
        conversation_key = f"{user_id}_{chat_id}"
        if conversation_key in self.active_conversations:
            del self.active_conversations[conversation_key]
            return True
        return False
