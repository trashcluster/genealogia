from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from config.settings import get_settings
import logging
import httpx
import os
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

class GenealogyBot:
    def __init__(self, conversation_engine):
        self.application = None
        self.conversation_engine = conversation_engine
        self.backend_url = settings.backend_service_url
        self.ingestion_url = settings.ingestion_service_url
        self.headers = {
            "Authorization": f"Bearer {settings.backend_api_key}"
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        await update.message.reply_text(
            "🌳 *Welcome to Genealogy Bot!* 👋\n\n"
            "I'm your intelligent family tree assistant! I can help you build a complete family tree through conversation.\n\n"
            "🤖 *What I can do:*\n"
            "• 📝 Chat about your family members\n"
            "• 🎤 Listen to voice stories\n"
            "• 📷 Analyze family photos\n"
            "• 📄 Process documents\n"
            "• 👤 Recognize faces in photos\n"
            "• 🤔 Ask smart questions\n"
            "• 📅 Extract events from calendars\n\n"
            "Just start talking about your family, and I'll guide you through the process!\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - Get detailed help\n"
            "/status - Check conversation status\n"
            "/reset - Start a new conversation",
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await update.message.reply_text(
            "📚 *Advanced Genealogy Bot Guide*\n\n"
            "🗣️ *Interactive Conversation*\n"
            "I'll ask you questions to build a complete family tree. Just answer naturally!\n\n"
            "📝 *Example conversations:*\n"
            "\"My grandfather John Smith was born in 1920 in London. He married Mary Johnson in 1945.\"\n\n"
            "🎤 *Voice Messages*\n"
            "Tell family stories and I'll extract names, dates, and relationships!\n\n"
            "📷 *Photos*\n"
            "Upload family photos and I'll:\n"
            "• Recognize family members\n"
            "• Extract text from documents\n"
            "• Correlate people with events\n\n"
            "📄 *Documents*\n"
            "Upload PDFs, images, or calendar files (.ics) for automatic processing.\n\n"
            "🤖 *Smart Features*\n"
            "• Face recognition to identify people\n"
            "• Event extraction from documents\n"
            "• Relationship suggestions\n"
            "• Timeline generation\n\n"
            "Just start sharing and I'll guide you! 🌟",
            parse_mode="Markdown"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        status = await self.conversation_engine.get_conversation_status(user_id, chat_id)
        
        if status:
            await update.message.reply_text(
                f"📊 *Conversation Status*\n\n"
                f"🔄 State: {status['state']}\n"
                f"⏱️ Duration: {status['session_duration']:.0f} seconds\n"
                f"❓ Questions remaining: {status['questions_remaining']}\n"
                f"👥 People collected: {status['data_collected']}\n\n"
                f"Type /reset to start a new conversation.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "No active conversation. Just start talking about your family! 🌳"
            )
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /reset command"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        success = await self.conversation_engine.end_conversation(user_id, chat_id)
        
        if success:
            await update.message.reply_text(
                "🔄 *Conversation reset*\n\n"
                "Let's start fresh! Tell me about your family members. 🌳",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "Ready to start! Tell me about your family members. 🌳"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages with conversation engine"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        
        await update.message.reply_text("🤔 Thinking... ⏳")
        
        try:
            # Process through conversation engine
            response = await self.conversation_engine.process_response(user_id, chat_id, message_text)
            
            await self._handle_conversation_response(update, response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        await update.message.reply_text("🎤 Processing your voice message... ⏳")
        
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_path = f"./uploads/{user_id}_voice_{voice_file.file_id}.ogg"
            os.makedirs("./uploads", exist_ok=True)
            await voice_file.download_to_drive(voice_path)
            
            # Transcribe and process
            async with httpx.AsyncClient() as client:
                with open(voice_path, 'rb') as f:
                    response = await client.post(
                        f"{self.ingestion_url}/api/ingest/voice",
                        files={"file": f},
                        timeout=60
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    transcript = data.get('raw_response', '')
                    
                    # Process transcript through conversation engine
                    response = await self.conversation_engine.process_response(user_id, chat_id, transcript)
                    
                    # Add transcript info
                    if isinstance(response, dict):
                        response["transcript"] = transcript
                    
                    await self._handle_conversation_response(update, response)
                else:
                    await update.message.reply_text("❌ Error processing voice message.")
            
            # Cleanup
            os.remove(voice_path)
        
        except Exception as e:
            logger.error(f"Error processing voice: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle documents (PDF, images, calendars)"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        document = update.message.document
        
        if document:
            await update.message.reply_text("📄 Processing your document... ⏳")
            
            try:
                # Download document
                doc_file = await document.get_file()
                doc_path = f"./uploads/{user_id}_{document.file_id}"
                os.makedirs("./uploads", exist_ok=True)
                await doc_file.download_to_drive(doc_path)
                
                # Determine file type and send to appropriate endpoint
                file_ext = os.path.splitext(document.file_name)[1].lower()
                
                if file_ext == '.pdf':
                    endpoint = "/api/ingest/pdf"
                elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    endpoint = "/api/ingest/image"
                elif file_ext in ['.ics', '.ical']:
                    endpoint = "/api/ingest/calendar"
                else:
                    os.remove(doc_path)
                    await update.message.reply_text(
                        "❌ Unsupported file format. Supported: PDF, JPG, PNG, GIF, BMP, ICS"
                    )
                    return
                
                async with httpx.AsyncClient() as client:
                    with open(doc_path, 'rb') as f:
                        response = await client.post(
                            f"{self.ingestion_url}{endpoint}",
                            files={"file": f},
                            timeout=60
                        )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # For images, also do face recognition
                        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                            face_response = await self._process_face_recognition(doc_path, user_id)
                            if face_response:
                                data["face_matches"] = face_response
                        
                        # Process extracted text through conversation engine
                        extracted_text = data.get('extracted_text', '') or data.get('raw_response', '')
                        if extracted_text:
                            response = await self.conversation_engine.process_response(user_id, chat_id, extracted_text)
                            
                            # Add document processing info
                            if isinstance(response, dict):
                                response["document_processed"] = document.file_name
                                response["extracted_entities"] = data.get('extracted_entities', [])
                            
                            await self._handle_conversation_response(update, response)
                        else:
                            await update.message.reply_text(
                                f"✅ Document processed: {document.file_name}\n\n"
                                "No text found to extract. Try uploading a document with readable text."
                            )
                    else:
                        await update.message.reply_text("❌ Error processing document.")
                
                os.remove(doc_path)
            
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photos with face recognition"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        await update.message.reply_text("📷 Analyzing photo... ⏳")
        
        try:
            # Get the largest photo
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            photo_path = f"./uploads/{user_id}_photo_{photo.file_id}.jpg"
            os.makedirs("./uploads", exist_ok=True)
            await photo_file.download_to_drive(photo_path)
            
            # Process face recognition
            face_response = await self._process_face_recognition(photo_path, user_id)
            
            # Extract text from photo (OCR)
            async with httpx.AsyncClient() as client:
                with open(photo_path, 'rb') as f:
                    response = await client.post(
                        f"{self.ingestion_url}/api/ingest/image",
                        files={"file": f},
                        timeout=60
                    )
                
                extracted_text = ""
                if response.status_code == 200:
                    data = response.json()
                    extracted_text = data.get('raw_response', '')
            
            # Build response
            message = "📷 *Photo Analysis Results*\n\n"
            
            if face_response and face_response.get("matches"):
                message += "👤 *Faces Recognized:*\n"
                for match in face_response["matches"][:3]:  # Limit to 3 matches
                    name = match.get("person_name", "Unknown")
                    confidence = match.get("similarity", 0) * 100
                    message += f"• {name} ({confidence:.0f}% confidence)\n"
                message += "\n"
            
            if extracted_text:
                message += f"📝 *Extracted Text:*\n{extracted_text[:200]}...\n\n"
                # Process through conversation engine
                response = await self.conversation_engine.process_response(user_id, chat_id, extracted_text)
                await self._handle_conversation_response(update, response)
            else:
                message += "No readable text found in this photo.\n\n"
                if face_response and face_response.get("matches"):
                    message += "But I found some familiar faces! 👤"
                else:
                    message += "Try uploading a photo with clearer text or recognizable faces."
                
                await update.message.reply_text(message, parse_mode="Markdown")
            
            os.remove(photo_path)
        
        except Exception as e:
            logger.error(f"Error processing photo: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        
        try:
            if query.data.startswith("confirm_"):
                # Handle confirmation
                await self.conversation_engine.process_response(user_id, chat_id, "confirm")
                await query.message.edit_text("✅ Confirmed! Processing your family tree...")
            
            elif query.data.startswith("edit_"):
                # Handle edit request
                await self.conversation_engine.process_response(user_id, chat_id, "edit")
                await query.message.edit_text("✏️ What would you like to change?")
            
            elif query.data.startswith("add_more_"):
                # Handle add more request
                await self.conversation_engine.process_response(user_id, chat_id, "add more")
                await query.message.edit_text("➕ What additional information would you like to share?")
        
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.message.edit_text("❌ Error processing your choice.")
    
    async def _handle_conversation_response(self, update: Update, response: dict) -> None:
        """Handle conversation engine responses"""
        
        status = response.get("status")
        
        if status == "questions_needed":
            message = f"🤔 {response['message']}\n\n"
            message += "❓ *Questions:*\n"
            for i, question in enumerate(response["questions"], 1):
                message += f"{i}. {question}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
        
        elif status == "continue_questions":
            message = f"✅ {response['message']}\n\n"
            message += "❓ *Next questions:*\n"
            for i, question in enumerate(response["questions"], 1):
                message += f"{i}. {question}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
        
        elif status == "confirmation_needed":
            message = f"✅ {response['message']}\n\n"
            message += f"📊 *Summary:*\n{response['summary']}\n\n"
            message += "🔘 *What would you like to do?*"
            
            # Create inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Confirm", callback_data="confirm_main"),
                    InlineKeyboardButton("✏️ Edit", callback_data="edit_main")
                ],
                [
                    InlineKeyboardButton("➕ Add More", callback_data="add_more_main")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
        
        elif status == "completed":
            message = f"🎉 {response['message']}\n\n"
            
            if "stored_data" in response:
                stored = response["stored_data"]
                if isinstance(stored, dict) and "individuals" in stored:
                    message += f"👥 Added {len(stored['individuals'])} people to your family tree!\n"
                if isinstance(stored, dict) and "families" in stored:
                    message += f"👨‍👩‍👧‍👦 Created {len(stored['families'])} family relationships!\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
        
        elif status == "add_more":
            message = f"➕ {response['message']}\n\n"
            if "suggestions" in response:
                message += "💡 *Suggestions:*\n"
                for suggestion in response["suggestions"]:
                    message += f"• {suggestion}\n"
            
            await update.message.reply_text(message, parse_mode="Markdown")
        
        else:
            # Handle other statuses
            message = response.get("message", "I'm processing your request...")
            await update.message.reply_text(message)
    
    async def _process_face_recognition(self, image_path: str, user_id: str) -> Optional[dict]:
        """Process face recognition for an image"""
        
        try:
            # Send to face recognition service
            async with httpx.AsyncClient() as client:
                with open(image_path, 'rb') as f:
                    response = await client.post(
                        "http://face-recognition:8004/match-faces",
                        files={"file": f},
                        timeout=30
                    )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Face recognition service error: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return None
    
    def setup(self):
        """Setup bot handlers"""
        self.application = Application.builder().token(settings.telegram_bot_token).build()
        
        # Commands
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))
        
        # Messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Callback queries
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        return self.application

async def main():
    """Start the bot"""
    from .conversation_engine import ConversationEngine
    
    conversation_engine = ConversationEngine(
        ingestion_service_url="http://ingestion:8001",
        backend_service_url="http://backend:8000"
    )
    
    bot = GenealogyBot(conversation_engine)
    app = bot.setup()
    
    # Start polling
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
